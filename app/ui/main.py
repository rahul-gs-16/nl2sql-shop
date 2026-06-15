"""
app/ui/app.py

Streamlit entry point for the NL-to-SQL Analytics Assistant.

Run with:
    streamlit run app/ui/app.py
"""

import logging
import pandas as pd
import streamlit as st
import json

from app.config import settings
from app.providers.factory import get_provider
from app.providers.health import validate_provider, is_ollama_available
from app.database.repository import validate_db_path, execute_query, get_column_names, place_order
from app.retrieval.store import initialize_store
from app.retrieval.seeder import seed_if_empty
from app.sql.generator import generate_sql

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Page config
# ---------------------------------------------------------------------------

st.set_page_config(
    page_title="Apple Store Chatbot",
    page_icon="📱",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------------------------------------------------------
# Startup validation (runs once per session via st.cache_resource)
# ---------------------------------------------------------------------------

@st.cache_resource(show_spinner="Initialising vector store...")
def _get_store():
    """Initialise ChromaDB store and seed with examples (once per session)."""
    store = initialize_store()
    seed_if_empty(store)
    return store


@st.cache_resource(show_spinner=False)
def _check_db():
    """Validate the database path and clear orders at startup."""
    validate_db_path()
    
    from app.database.repository import clear_orders
    clear_orders()
    
    return True


@st.cache_resource(show_spinner=False)
def _ollama_available():
    """Check once whether Ollama is reachable."""
    return is_ollama_available()


# ---------------------------------------------------------------------------
# Sidebar
# ---------------------------------------------------------------------------

with st.sidebar:
    st.title("⚙️ Configuration")
    st.markdown("---")

    ollama_ok = _ollama_available()

    provider_options = ["Gemini", "ChatGPT"]
    provider_map = {"Gemini": "gemini", "ChatGPT": "openai"}

    if ollama_ok:
        provider_options = ["Gemma (Local)", "Gemini", "ChatGPT"]
        provider_map["Gemma (Local)"] = "gemma"
    else:
        st.warning("Ollama is not available. Gemma (local) option is disabled.")

    # Default to the configured provider if it maps to an available option
    default_label = next(
        (k for k, v in provider_map.items() if v == settings.MODEL_PROVIDER),
        provider_options[0],
    )
    default_index = provider_options.index(default_label)

    selected_label = st.selectbox(
        "LLM Provider",
        options=provider_options,
        index=default_index,
        help="Select which language model to use.",
    )
    selected_provider_name = provider_map[selected_label]

    st.markdown("---")
    st.caption("Apple Store Assistant · demo build")

# ---------------------------------------------------------------------------
# Main area
# ---------------------------------------------------------------------------

st.title("📱 Apple Store Assistant")
st.markdown(
    "Ask a question about our iPhone inventory or place an order in plain English."
)

# DB startup validation (display error once if DB is missing)
try:
    _check_db()
except RuntimeError as db_err:
    st.error(f"**Database error:** {db_err}")
    st.stop()

# Initialise vector store
try:
    store = _get_store()
except Exception as store_err:
    st.error(f"**Vector store error:** {store_err}")
    st.stop()

# Validate the selected provider before the user submits a query
try:
    validate_provider(selected_provider_name)
    provider_valid = True
    provider_error = None
except (RuntimeError, ValueError) as prov_err:
    provider_valid = False
    provider_error = str(prov_err)

if not provider_valid:
    st.error(f"**Provider configuration error:** {provider_error}")

# ---------------------------------------------------------------------------
# Chat History Initialization
# ---------------------------------------------------------------------------

if "messages" not in st.session_state:
    st.session_state.messages = []

if "order_state" not in st.session_state:
    st.session_state.order_state = {}

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if "dataframe" in message:
            st.dataframe(message["dataframe"], use_container_width=True)

# ---------------------------------------------------------------------------
# Intent Routing Function
# ---------------------------------------------------------------------------

def route_intent(user_input: str, provider) -> dict:
    """
    Determine if the user wants to query data or place an order.
    Returns a dict with intent type and parameters.
    """
    history_text = "\n".join([f"{m['role']}: {m['content']}" for m in st.session_state.messages[-6:]]) if "messages" in st.session_state else ""
    current_order_state = json.dumps(st.session_state.order_state) if "order_state" in st.session_state else "{}"

    routing_prompt = f"""
    You are an intent classifier and entity extractor for an Apple mobile store.
    Determine if the user's LATEST message is an intent to PLACE AN ORDER, a QUERY for information, or a GREETING.
    
    Conversation History:
    {history_text}
    
    Current Known Order Details:
    {current_order_state}
    
    If it's a GREETING (like "hi", "hello", "help", etc.), return a JSON object like this:
    {{"intent": "greet"}}

    If the user asks for the PRICE of a phone (e.g. "what is the cost of iphone 16?") but does not specify the variant, color, or storage, return a JSON object like this to ask for clarification BEFORE querying the database:
    {{
      "intent": "clarify",
      "message": "To give you an accurate price, could you specify the variant (e.g., Pro, Standard) and storage capacity you are looking for?"
    }}
    (Note: Do NOT use 'clarify' if the user is explicitly asking what options/colors/storages are available, or asking for aggregate stats. Let those pass as 'query'.)

    If it's a clear QUERY that can be directly answered by the database, return a JSON object like this:
    {{"intent": "query"}}
    
    If it's an ORDER (or continuing an order by providing missing details), update the Current Known Order Details with any new information provided in the Latest User Message or implied from the Conversation History. Return a JSON object like this:
    {{
      "intent": "order",
      "customer_name": "extracted name or 'Unknown'",
      "contact_number": "extracted contact number or 'Unknown'",
      "address": "extracted address or 'Unknown'",
      "model": "MUST be strictly 'iPhone 15', 'iPhone 16', or 'iPhone 17' (DO NOT include the variant here)",
      "variant": "MUST be strictly 'Standard', 'Pro', or 'Pro Max'",
      "storage": "e.g., 256GB",
      "color": "e.g., Black",
      "quantity": 1,
      "confirmed": "MUST be true, false, or 'Unknown'"
    }}
    
    Rules for order extraction:
    - Retain existing details from Current Known Order Details unless the user explicitly overrides them.
    - Use the Conversation History to resolve implicit references (e.g. if the user says "order one for me", extract the product details discussed in the history).
    - If a parameter is not known and not mentioned, put 'Unknown'.
    - variant must be 'Standard', 'Pro', or 'Pro Max'. If a variant is not explicitly mentioned or clearly implied in the conversation history, put 'Unknown'. DO NOT assume 'Standard'.
    - model must NOT contain the variant. For example, if the user says "iPhone 16 Pro", model is "iPhone 16" and variant is "Pro".
    - confirmed MUST be true ONLY if the user explicitly confirms the final order details (e.g., "yes", "confirm"). MUST be false if they cancel (e.g., "no", "cancel"). Otherwise, put 'Unknown'.
    
    Latest User Message: "{user_input}"
    
    Return ONLY valid JSON. No markdown formatting or extra text.
    """
    
    try:
        raw_response = provider.generate(routing_prompt, temperature=0.0)
        # Clean up potential markdown from the LLM response
        cleaned_response = raw_response.strip().strip('`').replace('json\n', '', 1)
        intent_data = json.loads(cleaned_response)
        
        with open("debug.log", "a", encoding="utf-8") as f:
            f.write(f"USER INPUT: {user_input}\nINTENT JSON: {json.dumps(intent_data)}\n")
            
        return intent_data
    except Exception as e:
        logger.warning(f"Intent routing failed: {e}. Defaulting to query intent.")
        return {"intent": "query"}

def get_product_info(model, variant, color, storage):
    """Helper to lookup product ID and price before placing an order"""
    sql = f"SELECT id, price FROM products WHERE model = '{model}' AND variant = '{variant}' AND color = '{color}' AND storage = '{storage}'"
    try:
        rows = execute_query(sql)
        if rows:
            return rows[0]  # (id, price)
        return None
    except Exception:
        return None

# ---------------------------------------------------------------------------
# Chat Input & Processing
# ---------------------------------------------------------------------------

if prompt := st.chat_input("How can I help you?", disabled=not provider_valid):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # Display user message in chat message container
    with st.chat_message("user"):
        st.markdown(prompt)

    # Display assistant response in chat message container
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        
        try:
            provider = get_provider(selected_provider_name)
            
            with st.spinner("Analyzing intent..."):
                intent_data = route_intent(prompt, provider)
            
            if intent_data.get("intent") == "greet":
                response_text = "Hello! 👋 Welcome to the Apple Store. You can ask me to check our iPhone inventory, or directly place an order. How can I help you today?"
                message_placeholder.markdown(response_text)
                st.session_state.messages.append({"role": "assistant", "content": response_text})
                
            elif intent_data.get("intent") == "clarify":
                response_text = intent_data.get("message", "Could you please provide more details like the specific variant or storage capacity?")
                message_placeholder.markdown(response_text)
                st.session_state.messages.append({"role": "assistant", "content": response_text})
                
            elif intent_data.get("intent") == "order":
                # Handle Order Intent
                # Update session state with any new known values
                for k, v in intent_data.items():
                    if k != "intent" and v != "Unknown" and v is not None:
                        st.session_state.order_state[k] = v
                        
                name = st.session_state.order_state.get("customer_name", "Unknown")
                contact = st.session_state.order_state.get("contact_number", "Unknown")
                address = st.session_state.order_state.get("address", "Unknown")
                model = st.session_state.order_state.get("model", "Unknown")
                variant = st.session_state.order_state.get("variant", "Unknown")
                color = st.session_state.order_state.get("color", "Unknown")
                storage = st.session_state.order_state.get("storage", "Unknown")
                quantity = st.session_state.order_state.get("quantity", 1)
                
                missing_product = []
                if not model or model == "Unknown": missing_product.append("model (e.g. iPhone 15)")
                if not variant or variant == "Unknown": missing_product.append("variant (e.g. Pro, Standard)")
                if not color or color == "Unknown": missing_product.append("color")
                if not storage or storage == "Unknown": missing_product.append("storage capacity")
                
                missing_user = []
                if name == "Unknown": missing_user.append("name")
                if contact == "Unknown": missing_user.append("contact number")
                if address == "Unknown": missing_user.append("address")
                
                confirmed = st.session_state.order_state.get("confirmed", "Unknown")
                
                if confirmed is False or str(confirmed).lower() == "false":
                    st.session_state.order_state = {}
                    response_text = "Order cancelled. Let me know if you'd like to look at anything else!"
                    message_placeholder.markdown(response_text)
                    st.session_state.messages.append({"role": "assistant", "content": response_text})
                elif missing_product:
                    response_text = f"To place the order, I need to know the exact phone details. I am missing: {', '.join(missing_product)}. Please specify."
                    message_placeholder.markdown(response_text)
                    st.session_state.messages.append({"role": "assistant", "content": response_text})
                elif missing_user:
                    response_text = f"Almost ready! To complete the order, I just need your: {', '.join(missing_user)}."
                    message_placeholder.markdown(response_text)
                    st.session_state.messages.append({"role": "assistant", "content": response_text})
                elif confirmed != True and str(confirmed).lower() != "true":
                    # All details present, but not confirmed yet
                    with st.spinner("Fetching product details..."):
                        prod_info = get_product_info(model, variant, color, storage)
                        
                    if not prod_info:
                        response_text = f"Sorry, I couldn't find a {color} {model} {variant} with {storage} storage in our catalog."
                        message_placeholder.markdown(response_text)
                        st.session_state.messages.append({"role": "assistant", "content": response_text})
                    else:
                        prod_id, price = prod_info
                        total_price = price * quantity
                        response_text = f"""Please confirm your order details:
- **Product**: {model} {variant} {color} ({storage})
- **Price**: ${price:.2f} each (Total: **${total_price:.2f}**)
- **Quantity**: {quantity}
- **Name**: {name}
- **Contact**: {contact}
- **Address**: {address}

Reply **'Yes'** to confirm and place the order, or **'No'** to cancel."""
                        message_placeholder.markdown(response_text)
                        st.session_state.messages.append({"role": "assistant", "content": response_text})
                else:
                    with st.spinner("Processing order..."):
                        prod_info = get_product_info(model, variant, color, storage)
                        if prod_info:
                            result = place_order(name, contact, address, prod_info[0], quantity)
                            response_text = result["message"]
                            if result["success"]:
                                # Clear order state on success
                                st.session_state.order_state = {}
                        else:
                            response_text = f"Sorry, I couldn't find a {color} {model} {variant} with {storage} storage in our catalog."
                            
                    message_placeholder.markdown(response_text)
                    st.session_state.messages.append({"role": "assistant", "content": response_text})
                    
                    with open("debug.log", "a", encoding="utf-8") as f:
                        f.write(f"ORDER RESPONSE: {response_text}\n-----------------------\n")
            
            else:
                # Handle Query Intent (NL2SQL)
                with st.spinner(f"Searching inventory with **{selected_label}**..."):
                    # Optionally include some recent chat history in the prompt for context
                    history_context = ""
                    if len(st.session_state.messages) > 1:
                        history_context = "Recent conversation context:\n" + "\n".join(
                            [f"{m['role']}: {m['content']}" for m in st.session_state.messages[-5:-1]]
                        )
                    
                    full_query = f"{history_context}\n\nCurrent Question: {prompt}" if history_context else prompt
                    sql = generate_sql(full_query, provider, store)
                    
                    with open("debug.log", "a", encoding="utf-8") as f:
                        f.write(f"SQL GENERATED: {sql}\n")
                    
                with st.spinner("Executing query..."):
                    rows = execute_query(sql)
                    columns = get_column_names(sql)
                    
                df = pd.DataFrame(rows, columns=columns)
                
                with st.spinner("Generating response..."):
                    if not rows:
                        data_context = "The database query returned 0 results. This means we do not have what they asked for in stock."
                    else:
                        data_context = f"I ran a database query and got this data:\n{df.to_string(index=False)}"

                    nl_prompt = f"""
                    You are a helpful Apple Store assistant.
                    A user asked: "{prompt}"
                    
                    {data_context}
                    
                    Answer the user's question naturally and concisely based on the data context. 
                    - If the data contains an aggregate number (like a COUNT or SUM), use that number to directly answer the question (e.g. "Yes, we have 10 models available").
                    - If the data lists specific products, explicitly state whether they are in stock based on the 'stock' column.
                    - If multiple variants or colors are returned, you can briefly summarize what options we have available.
                    - Do not mention the database, SQL, or how you got the data.
                    """
                    nl_response = provider.generate(nl_prompt, temperature=0.3)
                    
                    with open("debug.log", "a", encoding="utf-8") as f:
                        f.write(f"NL RESPONSE: {nl_response}\n-----------------------\n")
                    
                message_placeholder.markdown(nl_response)
                
                st.session_state.messages.append({
                    "role": "assistant", 
                    "content": nl_response
                })
                    
        except ValueError as ve:
            # Task 7.6 — user-readable error (e.g. read-only violation)
            error_msg = f"**Query validation error:** {ve}"
            message_placeholder.error(error_msg)
            st.session_state.messages.append({"role": "assistant", "content": error_msg})
            
        except Exception as exc:
            # Task 7.6 — catch-all: no traceback shown to user
            logger.exception("Unhandled error during query execution")
            error_msg = f"**An error occurred:** {exc}\nPlease try rephrasing your question or check the provider configuration."
            message_placeholder.error(error_msg)
            st.session_state.messages.append({"role": "assistant", "content": error_msg})
