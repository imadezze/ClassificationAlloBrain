"""Model Selector Component - Select LLM provider and model"""
import streamlit as st
from typing import Dict, List, Tuple
import logging
from src.config import Config

logger = logging.getLogger(__name__)


# Latest models by provider (from LiteLLM docs - Feb 2026)
ANTHROPIC_MODELS = {
    # Claude 4.5 Series (Latest)
    "claude-opus-4-5-20251101": {
        "name": "Claude Opus 4.5",
        "description": "Most capable model - best for complex tasks",
        "released": "Nov 2025"
    },
    "claude-sonnet-4-5-20250929": {
        "name": "Claude Sonnet 4.5",
        "description": "Balanced performance - great for coding",
        "released": "Sep 2025"
    },
    # Claude 3.7
    "claude-3-7-sonnet-20250219": {
        "name": "Claude 3.7 Sonnet",
        "description": "Enhanced 3.x model",
        "released": "Feb 2025"
    },
    # Claude 3.5
    "claude-3-5-sonnet-20240620": {
        "name": "Claude 3.5 Sonnet",
        "description": "Previous generation flagship",
        "released": "Jun 2024"
    },
    # Claude 3 Base
    "claude-3-opus-20240229": {
        "name": "Claude 3 Opus",
        "description": "Original Claude 3 - most capable",
        "released": "Feb 2024"
    },
    "claude-3-sonnet-20240229": {
        "name": "Claude 3 Sonnet",
        "description": "Balanced Claude 3",
        "released": "Feb 2024"
    },
    "claude-3-haiku-20240307": {
        "name": "Claude 3 Haiku",
        "description": "Fastest Claude 3",
        "released": "Mar 2024"
    },
}

OPENAI_MODELS = {
    # GPT-5 Series (Latest)
    "gpt-5.2-2025-12-11": {
        "name": "GPT-5.2 (Dec 2025)",
        "description": "Latest dated release - DEFAULT",
        "released": "Dec 11, 2025"
    },
    "gpt-5.2": {
        "name": "GPT-5.2",
        "description": "Latest versioned release",
        "released": "2025"
    },
    "gpt-5.1": {
        "name": "GPT-5.1",
        "description": "Previous versioned release",
        "released": "2025"
    },
    "gpt-5": {
        "name": "GPT-5",
        "description": "Latest flagship model",
        "released": "2025"
    },
    "gpt-5-pro": {
        "name": "GPT-5 Pro",
        "description": "Advanced reasoning capabilities",
        "released": "2025"
    },
    "gpt-5-mini": {
        "name": "GPT-5 Mini",
        "description": "Efficient latest generation",
        "released": "2025"
    },
    # GPT-4o Series
    "gpt-4o": {
        "name": "GPT-4o",
        "description": "Multimodal flagship model",
        "released": "2024"
    },
    "gpt-4o-mini": {
        "name": "GPT-4o Mini",
        "description": "Lightweight multimodal",
        "released": "2024"
    },
    # GPT-4.1 Series
    "gpt-4.1": {
        "name": "GPT-4.1",
        "description": "Enhanced GPT-4 generation",
        "released": "2025"
    },
    "gpt-4.1-mini": {
        "name": "GPT-4.1 Mini",
        "description": "Efficient GPT-4.1 variant",
        "released": "2025"
    },
    "gpt-4.1-nano": {
        "name": "GPT-4.1 Nano",
        "description": "Lightweight GPT-4.1",
        "released": "2025"
    },
    # GPT-4 Turbo
    "gpt-4-turbo": {
        "name": "GPT-4 Turbo",
        "description": "High-performance GPT-4",
        "released": "2024"
    },
}


def get_current_provider_and_model() -> Tuple[str, str]:
    """
    Get current provider and model from session state or config

    Returns:
        Tuple of (provider, model_id)
    """
    current_model = st.session_state.get("selected_model", Config.LLM_MODEL)

    # Determine provider
    if current_model in ANTHROPIC_MODELS:
        return ("Anthropic", current_model)
    elif current_model in OPENAI_MODELS:
        return ("OpenAI", current_model)
    else:
        # Default to OpenAI if unknown
        return ("OpenAI", "gpt-4o")


def render_model_selector(location: str = "sidebar") -> str:
    """
    Render model selector with provider tabs

    Args:
        location: Where to render ("sidebar" or "main")

    Returns:
        Selected model ID
    """
    container = st.sidebar if location == "sidebar" else st

    with container:
        st.subheader("🤖 Model Selection")

        # Initialize session state
        if "selected_model" not in st.session_state:
            st.session_state.selected_model = Config.LLM_MODEL

        # Get current provider and model
        current_provider, current_model = get_current_provider_and_model()

        # Provider tabs
        provider_tabs = st.tabs(["🔷 Anthropic", "🟢 OpenAI"])

        # Anthropic Tab
        with provider_tabs[0]:
            st.caption("**Claude Models**")

            # Find current selection index
            anthropic_models = list(ANTHROPIC_MODELS.keys())
            current_index = 0
            if current_provider == "Anthropic" and current_model in anthropic_models:
                current_index = anthropic_models.index(current_model)

            selected_anthropic = st.radio(
                "Select Claude Model",
                options=anthropic_models,
                index=current_index,
                format_func=lambda x: f"{ANTHROPIC_MODELS[x]['name']} - {ANTHROPIC_MODELS[x]['description']}",
                key="anthropic_model_selector",
                label_visibility="collapsed"
            )

            # Show model details
            model_info = ANTHROPIC_MODELS[selected_anthropic]
            st.caption(f"📅 Released: {model_info['released']}")
            st.caption(f"🆔 Model ID: `{selected_anthropic}`")

            if st.button("✓ Use This Model", key="use_anthropic", use_container_width=True, type="primary"):
                st.session_state.selected_model = selected_anthropic
                st.success(f"✓ Switched to {model_info['name']}")
                st.rerun()

        # OpenAI Tab
        with provider_tabs[1]:
            st.caption("**GPT Models**")

            # Find current selection index
            openai_models = list(OPENAI_MODELS.keys())
            current_index = 0
            if current_provider == "OpenAI" and current_model in openai_models:
                current_index = openai_models.index(current_model)

            selected_openai = st.radio(
                "Select GPT Model",
                options=openai_models,
                index=current_index,
                format_func=lambda x: f"{OPENAI_MODELS[x]['name']} - {OPENAI_MODELS[x]['description']}",
                key="openai_model_selector",
                label_visibility="collapsed"
            )

            # Show model details
            model_info = OPENAI_MODELS[selected_openai]
            st.caption(f"📅 Released: {model_info['released']}")
            st.caption(f"🆔 Model ID: `{selected_openai}`")

            if st.button("✓ Use This Model", key="use_openai", use_container_width=True, type="primary"):
                st.session_state.selected_model = selected_openai
                st.success(f"✓ Switched to {model_info['name']}")
                st.rerun()

        # Show current active model
        st.divider()
        current_provider, current_model = get_current_provider_and_model()

        if current_provider == "Anthropic":
            model_info = ANTHROPIC_MODELS.get(current_model, {"name": current_model, "description": "Unknown"})
        else:
            model_info = OPENAI_MODELS.get(current_model, {"name": current_model, "description": "Unknown"})

        st.write("**Currently Active:**")
        st.info(f"🎯 {model_info['name']}\n\n`{current_model}`")

        # Advanced settings - editable
        with st.expander("⚙️ Advanced Settings", expanded=False):
            st.caption("Adjust LLM parameters for classification")

            # Initialize session state for settings
            if "llm_temperature" not in st.session_state:
                st.session_state.llm_temperature = Config.LLM_TEMPERATURE
            if "llm_max_tokens" not in st.session_state:
                st.session_state.llm_max_tokens = Config.LLM_MAX_TOKENS

            # Temperature slider
            temperature = st.slider(
                "🌡️ Temperature",
                min_value=0.0,
                max_value=2.0,
                value=st.session_state.llm_temperature,
                step=0.1,
                help="Lower = more focused/deterministic, Higher = more creative/random"
            )

            # Show temperature guidance
            if temperature <= 0.2:
                st.caption("🎯 Very focused - Best for classification")
            elif temperature <= 0.5:
                st.caption("⚖️ Balanced")
            elif temperature <= 1.0:
                st.caption("🎨 Creative")
            else:
                st.caption("🎲 Very random")

            # Max tokens slider
            max_tokens = st.slider(
                "📏 Max Tokens",
                min_value=100,
                max_value=4000,
                value=st.session_state.llm_max_tokens,
                step=100,
                help="Maximum length of LLM response"
            )

            # Apply button
            if temperature != st.session_state.llm_temperature or max_tokens != st.session_state.llm_max_tokens:
                st.info(f"💡 Changes pending: Temperature: {temperature}, Max Tokens: {max_tokens}")

                col1, col2 = st.columns(2)

                with col1:
                    if st.button("✓ Apply", key="apply_settings", use_container_width=True, type="primary"):
                        st.session_state.llm_temperature = temperature
                        st.session_state.llm_max_tokens = max_tokens
                        st.success("✓ Settings updated!")
                        st.rerun()

                with col2:
                    if st.button("↺ Reset", key="reset_settings", use_container_width=True):
                        st.session_state.llm_temperature = Config.LLM_TEMPERATURE
                        st.session_state.llm_max_tokens = Config.LLM_MAX_TOKENS
                        st.rerun()
            else:
                st.success("✓ Current settings applied")

        return st.session_state.selected_model


def get_selected_model() -> str:
    """
    Get the currently selected model

    Returns:
        Model identifier string
    """
    return st.session_state.get("selected_model", Config.LLM_MODEL)
