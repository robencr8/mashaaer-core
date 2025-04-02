"""
AI Model Router for Robin AI
Routes requests to different AI models based on configuration settings.
Supports OpenAI API and Ollama local models with graceful fallbacks.
"""
import json
import logging
import os
import time
from typing import Any, Dict, List, Optional

import requests

# Set up logging
logger = logging.getLogger(__name__)

class AIModelRouter:
    """
    Routes AI requests to different models based on environment configuration
    and handles fallbacks automatically when models are unavailable.
    """
    
    def __init__(self):
        """Initialize the AI Model Router with configuration from environment variables"""
        # Load configuration from environment variables
        self.model_backend = os.environ.get("MODEL_BACKEND", "").lower()
        self.ollama_base_url = os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434")
        self.openai_api_key = os.environ.get("OPENAI_API_KEY", "")
        
        # Supported models
        self.ollama_models = ["openchat", "mistral", "phi"]
        self.openai_models = ["gpt-4", "gpt-4o"]
        
        # Usage metrics
        self.request_count = 0
        self.error_count = 0
        self.last_model_used = None
        self.last_request_time = None
        
        # Log the configuration
        self._log_configuration()
    
    def _log_configuration(self):
        """Log the current configuration (excluding sensitive keys)"""
        logger.info("AI Model Router Configuration:")
        logger.info(f"- MODEL_BACKEND: {self.model_backend}")
        logger.info(f"- OLLAMA_BASE_URL: {self.ollama_base_url}")
        logger.info(f"- Supported Ollama Models: {', '.join(self.ollama_models)}")
        logger.info(f"- Supported OpenAI Models: {', '.join(self.openai_models)}")
        logger.info(f"- OpenAI API Key: {'Configured' if self.openai_api_key else 'Not configured'}")
        
        # Additional information for auto mode
        if self.model_backend == "auto":
            if self.openai_api_key and self.is_ollama_running():
                logger.info("- Using AUTO mode: Will try OpenAI first, then Ollama as fallback")
            elif self.openai_api_key:
                logger.info("- Using AUTO mode: Will use OpenAI (Ollama not detected)")
            elif self.is_ollama_running():
                logger.info("- Using AUTO mode: Will use Ollama (OpenAI key not configured)")
            else:
                logger.warning("- Using AUTO mode: No AI backends detected! Emergency fallback will be used.")
    
    def _is_model_supported(self, model: str) -> bool:
        """Check if the specified model is supported"""
        if not model:
            return False
        return (model.lower() in [m.lower() for m in self.ollama_models] or
                model.lower() in [m.lower() for m in self.openai_models])
    
    def get_default_model(self) -> str:
        """Get the default model based on configuration"""
        # If model_backend is set, use it to determine default model
        if self.model_backend == "auto":
            # For auto mode, return based on availability preference
            if self.openai_api_key:
                return "gpt-4o"  # Prefer OpenAI when available in auto mode
            elif self.is_ollama_running():
                return self.ollama_models[0]
            else:
                return "auto"  # Special value indicating auto mode with no models
        elif self.model_backend == "ollama" and self.is_ollama_running():
            return self.ollama_models[0]  # First Ollama model (openchat)
        elif self.model_backend == "openai" and self.openai_api_key:
            return "gpt-4o"  # Prefer the latest GPT-4o model
        
        # If no specific backend is set, choose based on availability
        if self.is_ollama_running():
            return self.ollama_models[0]
        elif self.openai_api_key:
            return "gpt-4o"
        
        # Fallback to a supported model even if not available
        return "openchat"
    
    def is_ollama_running(self) -> bool:
        """Check if Ollama is running and accessible"""
        try:
            response = requests.get(f"{self.ollama_base_url}/api/tags", timeout=2)
            return response.status_code == 200
        except Exception:
            return False
    
    def get_available_models(self) -> Dict[str, List[str]]:
        """Get lists of available models"""
        available_models = {}
        
        # Check Ollama models
        if self.is_ollama_running():
            try:
                response = requests.get(f"{self.ollama_base_url}/api/tags", timeout=3)
                if response.status_code == 200:
                    models_data = response.json()
                    available_ollama_models = []
                    
                    # Get all models from Ollama that we support
                    for model in models_data.get("models", []):
                        model_name = model.get("name", "").split(":")[0]
                        if model_name.lower() in [m.lower() for m in self.ollama_models]:
                            available_ollama_models.append(model_name)
                    
                    available_models["ollama"] = available_ollama_models
            except Exception as e:
                logger.error(f"Error getting Ollama models: {e}")
        
        # Check OpenAI models
        if self.openai_api_key:
            available_models["openai"] = self.openai_models
        
        return available_models
    
    def complete_with_ollama(
        self, 
        prompt: str, 
        model: str = "openchat",
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 1000,
        stream: bool = False
    ) -> Dict[str, Any]:
        """
        Complete text using Ollama local model
        
        Args:
            prompt: The user's input text
            model: The Ollama model to use
            system_prompt: Optional system prompt to guide the model
            temperature: Controls randomness (0.0 to 1.0)
            max_tokens: Maximum number of tokens to generate
            stream: Whether to stream the response
            
        Returns:
            Dict with response content and metadata
        """
        # Validate model exists in Ollama
        if not self.is_ollama_running():
            return {
                "success": False,
                "error": "Ollama is not running or accessible",
                "model": model,
                "timestamp": time.time(),
                "content": None,
                "error_type": "service_unavailable"
            }
        
        # Prepare request
        system = system_prompt if system_prompt else "You are Robin AI, a helpful and friendly assistant."
        
        payload = {
            "model": model,
            "prompt": prompt,
            "system": system,
            "stream": stream,
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens
            }
        }
        
        try:
            response = requests.post(
                f"{self.ollama_base_url}/api/generate",
                json=payload,
                timeout=30  # 30 second timeout for generation
            )
            
            if response.status_code != 200:
                error_msg = f"Ollama API error: {response.status_code}"
                try:
                    error_data = response.json()
                    if "error" in error_data:
                        error_msg = error_data["error"]
                except Exception:
                    pass
                
                return {
                    "success": False,
                    "error": error_msg,
                    "model": model,
                    "timestamp": time.time(),
                    "content": None,
                    "error_type": "api_error"
                }
            
            result = response.json()
            
            # Update usage metrics
            self.request_count += 1
            self.last_model_used = model
            self.last_request_time = time.time()
            
            return {
                "success": True,
                "content": result.get("response", ""),
                "model": model,
                "timestamp": time.time(),
                "context": result.get("context", []),
                "done": result.get("done", True)
            }
            
        except Exception as e:
            logger.error(f"Error calling Ollama API: {str(e)}")
            # Update error metrics
            self.error_count += 1
            
            return {
                "success": False,
                "error": f"Error calling Ollama API: {str(e)}",
                "model": model,
                "timestamp": time.time(),
                "content": None,
                "error_type": "api_exception"
            }
    
    def complete_with_openai(
        self,
        prompt: str,
        model: str = "gpt-4o",
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 1000,
        stream: bool = False
    ) -> Dict[str, Any]:
        """
        Complete text using OpenAI API
        
        Args:
            prompt: The user's input text
            model: The OpenAI model to use
            system_prompt: Optional system prompt to guide the model
            temperature: Controls randomness (0.0 to 1.0)
            max_tokens: Maximum tokens to generate
            stream: Whether to stream the response
            
        Returns:
            Dict with response content and metadata
        """
        if not self.openai_api_key:
            return {
                "success": False,
                "error": "OpenAI API key not configured",
                "model": model,
                "timestamp": time.time(),
                "content": None,
                "error_type": "missing_api_key"
            }
        
        # Use actual OpenAI client for better reliability
        try:
            from openai import OpenAI
            client = OpenAI(api_key=self.openai_api_key)
            
            # Default system prompt if not provided
            system = system_prompt if system_prompt else "You are Robin AI, a helpful and friendly assistant."
            
            # Create completion request
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": system},
                    {"role": "user", "content": prompt}
                ],
                temperature=temperature,
                max_tokens=max_tokens,
                stream=stream
            )
            
            # Process the response based on whether streaming is enabled
            if stream:
                # For streaming, return a generator (not implemented here)
                return {
                    "success": False,
                    "error": "Streaming not implemented for OpenAI",
                    "model": model,
                    "timestamp": time.time(),
                    "content": None,
                    "error_type": "not_implemented"
                }
            else:
                # For regular response
                content = response.choices[0].message.content
                
                # Update usage metrics
                self.request_count += 1
                self.last_model_used = model
                self.last_request_time = time.time()
                
                return {
                    "success": True,
                    "content": content,
                    "model": model,
                    "timestamp": time.time(),
                    "usage": {
                        "prompt_tokens": response.usage.prompt_tokens,
                        "completion_tokens": response.usage.completion_tokens,
                        "total_tokens": response.usage.total_tokens
                    },
                    "finish_reason": response.choices[0].finish_reason
                }
                
        except Exception as e:
            logger.error(f"Error calling OpenAI API: {str(e)}")
            # Update error metrics
            self.error_count += 1
            
            return {
                "success": False,
                "error": f"Error calling OpenAI API: {str(e)}",
                "model": model,
                "timestamp": time.time(),
                "content": None,
                "error_type": "api_exception"
            }
    
    def generate_response(
        self,
        prompt: str,
        model: Optional[str] = None,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 1000,
        stream: bool = False
    ) -> Dict[str, Any]:
        """
        Generate AI response using the configured model backend
        
        Args:
            prompt: The user's input text
            model: Optional specific model to use (overrides MODEL_BACKEND)
            system_prompt: Optional system instructions for the model
            temperature: Controls randomness (0.0 to 1.0)
            max_tokens: Maximum tokens to generate
            stream: Whether to stream the response
            
        Returns:
            Dict with response content and metadata
        """
        # Start time for tracking
        start_time = time.time()
        
        # If model is specified, try to use it directly
        if model:
            if model.lower() in [m.lower() for m in self.ollama_models]:
                # Use Ollama for this model
                result = self.complete_with_ollama(
                    prompt=prompt,
                    model=model,
                    system_prompt=system_prompt,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    stream=stream
                )
                
                # If successful, return the result
                if result["success"]:
                    logger.info(f"Generated response using specified model: {model} in {time.time() - start_time:.2f}s")
                    return result
                
                # If failed, log the error and try fallback to OpenAI
                logger.warning(f"Failed to use specified Ollama model: {model}, error: {result.get('error', 'unknown error')}")
                
                # Only attempt OpenAI fallback if we have an API key
                if self.openai_api_key:
                    logger.info(f"Falling back to OpenAI for model: {model}")
                    fallback_model = "gpt-4o"
                    result = self.complete_with_openai(
                        prompt=prompt,
                        model=fallback_model,
                        system_prompt=system_prompt,
                        temperature=temperature,
                        max_tokens=max_tokens,
                        stream=stream
                    )
                    
                    if result["success"]:
                        logger.info(f"Generated response using fallback OpenAI model: {fallback_model} in {time.time() - start_time:.2f}s")
                        result["original_model"] = model
                        result["fallback"] = True
                        return result
                    
                    # If OpenAI also failed, return the Ollama error
                    logger.error(f"Both specified model and fallback failed. Model: {model}, fallback: {fallback_model}")
                    return result
                
                # No OpenAI API key, so just return the Ollama error
                return result
                
            elif model.lower() in [m.lower() for m in self.openai_models]:
                # Use OpenAI for this model
                result = self.complete_with_openai(
                    prompt=prompt,
                    model=model,
                    system_prompt=system_prompt,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    stream=stream
                )
                
                # If successful, return the result
                if result["success"]:
                    logger.info(f"Generated response using specified model: {model} in {time.time() - start_time:.2f}s")
                    return result
                
                # If failed, log the error and try fallback to Ollama
                logger.warning(f"Failed to use specified OpenAI model: {model}, error: {result.get('error', 'unknown error')}")
                
                # Only attempt Ollama fallback if it's running
                if self.is_ollama_running():
                    logger.info(f"Falling back to Ollama for model: {model}")
                    fallback_model = self.ollama_models[0]  # Use first Ollama model as fallback
                    result = self.complete_with_ollama(
                        prompt=prompt,
                        model=fallback_model,
                        system_prompt=system_prompt,
                        temperature=temperature,
                        max_tokens=max_tokens,
                        stream=stream
                    )
                    
                    if result["success"]:
                        logger.info(f"Generated response using fallback Ollama model: {fallback_model} in {time.time() - start_time:.2f}s")
                        result["original_model"] = model
                        result["fallback"] = True
                        return result
                    
                    # If Ollama also failed, return the OpenAI error
                    logger.error(f"Both specified model and fallback failed. Model: {model}, fallback: {fallback_model}")
                    return result
                
                # Ollama not running, so just return the OpenAI error
                return result
            
            else:
                # Unknown model, report error
                error = f"Unknown model: {model}. Supported models: {', '.join(self.ollama_models + self.openai_models)}"
                logger.error(error)
                return {
                    "success": False,
                    "error": error,
                    "model": model,
                    "timestamp": time.time(),
                    "content": None,
                    "error_type": "unknown_model"
                }
        
        # No specific model provided, use configured backend
        if self.model_backend == "auto":
            # Auto mode - try both backends based on availability
            if self.openai_api_key:
                # If OpenAI is configured, try it first (typically better quality)
                logger.info("Using auto mode, trying OpenAI first")
                model_to_use = "gpt-4o"
                result = self.complete_with_openai(
                    prompt=prompt,
                    model=model_to_use,
                    system_prompt=system_prompt,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    stream=stream
                )
                
                # If successful, return the result
                if result["success"]:
                    logger.info(f"Generated response using OpenAI model: {model_to_use} in {time.time() - start_time:.2f}s")
                    return result
                
                # If failed and Ollama is running, try that as fallback
                if self.is_ollama_running():
                    logger.info("OpenAI failed in auto mode, trying Ollama")
                    fallback_model = self.ollama_models[0]
                    result = self.complete_with_ollama(
                        prompt=prompt,
                        model=fallback_model,
                        system_prompt=system_prompt,
                        temperature=temperature,
                        max_tokens=max_tokens,
                        stream=stream
                    )
                    
                    if result["success"]:
                        logger.info(f"Generated response using fallback Ollama model: {fallback_model} in {time.time() - start_time:.2f}s")
                        result["original_model"] = model_to_use
                        result["fallback"] = True
                        return result
                
                # Both failed, return last error
                return result
            
            # If OpenAI not configured, try Ollama
            elif self.is_ollama_running():
                logger.info("Using auto mode, OpenAI not configured, trying Ollama")
                model_to_use = self.ollama_models[0]
                result = self.complete_with_ollama(
                    prompt=prompt,
                    model=model_to_use,
                    system_prompt=system_prompt,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    stream=stream
                )
                
                if result["success"]:
                    logger.info(f"Generated response using Ollama model: {model_to_use} in {time.time() - start_time:.2f}s")
                    return result
                
                # Ollama failed, no OpenAI fallback available
                return result
            
            # No backends available in auto mode
            error = "No AI model backends available in auto mode. Please configure OPENAI_API_KEY or ensure Ollama is running."
            logger.error(error)
            return {
                "success": False,
                "error": error,
                "model": "auto",
                "timestamp": time.time(),
                "content": None,
                "error_type": "no_backends_available_auto"
            }
                
        elif self.model_backend == "ollama" or (not self.model_backend and self.is_ollama_running()):
            # Try Ollama first
            model_to_use = self.ollama_models[0]  # Default to first model in list
            result = self.complete_with_ollama(
                prompt=prompt,
                model=model_to_use,
                system_prompt=system_prompt,
                temperature=temperature,
                max_tokens=max_tokens,
                stream=stream
            )
            
            # If successful, return the result
            if result["success"]:
                logger.info(f"Generated response using Ollama model: {model_to_use} in {time.time() - start_time:.2f}s")
                return result
            
            # If failed and we have OpenAI configured, try that as fallback
            if self.openai_api_key:
                logger.info(f"Ollama failed, falling back to OpenAI")
                fallback_model = "gpt-4o"
                result = self.complete_with_openai(
                    prompt=prompt,
                    model=fallback_model,
                    system_prompt=system_prompt,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    stream=stream
                )
                
                if result["success"]:
                    logger.info(f"Generated response using fallback OpenAI model: {fallback_model} in {time.time() - start_time:.2f}s")
                    result["original_model"] = model_to_use
                    result["fallback"] = True
                    return result
            
            # All fallbacks failed or not available
            return result
            
        elif self.model_backend == "openai" or (not self.model_backend and self.openai_api_key):
            # Try OpenAI first
            model_to_use = "gpt-4o"  # Default to GPT-4o (current best)
            result = self.complete_with_openai(
                prompt=prompt,
                model=model_to_use,
                system_prompt=system_prompt,
                temperature=temperature,
                max_tokens=max_tokens,
                stream=stream
            )
            
            # If successful, return the result
            if result["success"]:
                logger.info(f"Generated response using OpenAI model: {model_to_use} in {time.time() - start_time:.2f}s")
                return result
            
            # If failed and Ollama is running, try that as fallback
            if self.is_ollama_running():
                logger.info(f"OpenAI failed, falling back to Ollama")
                fallback_model = self.ollama_models[0]
                result = self.complete_with_ollama(
                    prompt=prompt,
                    model=fallback_model,
                    system_prompt=system_prompt,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    stream=stream
                )
                
                if result["success"]:
                    logger.info(f"Generated response using fallback Ollama model: {fallback_model} in {time.time() - start_time:.2f}s")
                    result["original_model"] = model_to_use
                    result["fallback"] = True
                    return result
            
            # All fallbacks failed or not available
            return result
        
        # No available models or backends
        error = "No AI model backends available. Please configure MODEL_BACKEND or OPENAI_API_KEY."
        logger.error(error)
        
        # Provide a simple fallback response when no AI services are available
        # This ensures the application doesn't completely break when offline
        if "hello" in prompt.lower() or "hi" in prompt.lower() or "how are you" in prompt.lower():
            fallback_content = "Hello! I'm Robin AI. I'm currently running in offline mode, so my responses are limited. The AI model service is currently unavailable."
        else:
            fallback_content = "I'm sorry, I can't process your request at the moment. The AI model service is unavailable. Please check the configuration and try again later."
        
        logger.warning(f"Using emergency fallback response for query: {prompt[:50]}...")
        
        return {
            "success": True,  # Mark as success so the application continues functioning
            "error": error,
            "model": "fallback",
            "timestamp": time.time(),
            "content": fallback_content,
            "error_type": "no_backends_available",
            "fallback": True
        }
    
    def get_status(self) -> Dict[str, Any]:
        """Get the current status of the AI Model Router"""
        # Get current status of backends
        ollama_running = self.is_ollama_running()
        openai_configured = bool(self.openai_api_key)
        
        # Get available models
        available_models = self.get_available_models()
        
        # Prepare status response
        status = {
            "model_backend": self.model_backend,
            "ollama_running": ollama_running,
            "openai_configured": openai_configured,
            "available_models": available_models,
            "request_count": self.request_count,
            "error_count": self.error_count,
            "last_model_used": self.last_model_used,
            "last_request_time": self.last_request_time
        }
        
        return status