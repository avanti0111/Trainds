import os
import datetime
from app.services.graph_service import get_graph
from app.services.ml_service import predict_delay
from app.services.weather_service import get_weather_data

def get_fastest_route(source: str, destination: str) -> str:
    """Finds the fastest train route between two stations. Call this when the user asks how to go from one place to another."""
    try:
        graph = get_graph()
        result = graph.dijkstra(source, destination)
        if result and "route" in result:
            time_min = result.get("total_time_min", 0)
            path = " -> ".join(result["route"])
            return f"Route found: {path}. Total time: {time_min} mins."
        return f"Could not find a valid route between {source} and {destination}."
    except Exception as e:
        return f"Error finding route: {str(e)}"

def get_delay_prediction(station: str) -> str:
    """Predicts train delays at a given station using the AI model. Call this when the user asks about delays, lateness, or weather issues at a station."""
    try:
        now = datetime.datetime.now()
        weather_payload = get_weather_data(station)
        val = predict_delay(now.hour, now.weekday(), weather_payload.get('condition','Clear'), weather_payload.get('rainfall', 0.0), station=station)
        
        risk = val.get("risk_level", "Low")
        mins = val.get("predicted_delay_min", 0)
        factors = ', '.join(val.get('factors', []))
        return f"At {station}, expected delay is {mins} minutes (Risk: {risk}). Factors: {factors}."
    except Exception as e:
        return f"Error checking delays: {str(e)}"

def get_available_stations() -> str:
    """Returns a list of all valid stations in the Mumbai local train network. Call this if you need to know exact station names."""
    try:
        graph = get_graph()
        return ", ".join([str(s) for s in getattr(graph, 'stations', [])])
    except Exception as e:
        return ""

def process_chat_query(message: str, history: list = None) -> str:
    from dotenv import load_dotenv
    load_dotenv(override=True)
    
    if history is None:
        history = []
        
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return "To unlock my full AI capabilities and allow me to understand complex queries like 'from gtb to sion', please add your GEMINI_API_KEY to the backend .env file!"
        
    try:
        import google.generativeai as genai
        genai.configure(api_key=api_key)
        
        system_instruction = (
            "You are TRAiNDS AI, an expert and highly helpful assistant for the Mumbai local train network. "
            "You have access to tools that can find routes and predict delays. "
            "When a user asks for a route, ALWAYS use the get_fastest_route tool. "
            "If a user uses abbreviations (like 'gtb' for 'GTB Nagar', 'cst' for 'CSMT'), map them to the correct station name before calling tools. "
            "Respond in a friendly, conversational manner. Keep your answers concise and directly answer the user's question."
        )
        
        model = genai.GenerativeModel(
            model_name='gemini-flash-latest',
            tools=[get_fastest_route, get_delay_prediction, get_available_stations],
            system_instruction=system_instruction
        )
        
        chat = model.start_chat(history=history, enable_automatic_function_calling=True)
        response = chat.send_message(message)
        return response.text
    except Exception as e:
        return f"I encountered an error connecting to my AI brain: {str(e)}"
