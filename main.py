from fastapi import FastAPI, Request
import requests
import os
import uvicorn

app = FastAPI()

# Récupération des variables d'environnement (assure-toi qu'elles sont bien définies sur Railway)
KLAVIYO_API_KEY = os.getenv("KLAVIYO_API_KEY")
KLAVIYO_LIST_ID = os.getenv("KLAVIYO_LIST_ID")

@app.post("/webhook/deliverect/")
async def receive_deliverect_order(request: Request):
    """Réception des commandes de Deliverect et envoi des infos à Klaviyo"""
    order_data = await request.json()
    customer_email = order_data.get("customer", {}).get("email", "")
    customer_name = order_data.get("customer", {}).get("name", "")
    products = [item["name"] for item in order_data.get("orderItems", [])]

    if not customer_email:
        return {"status": "error", "message": "Pas d'email client fourni"}

    klaviyo_response = send_to_klaviyo(customer_email, customer_name, products)
    
    return {"status": "success", "klaviyo_response": klaviyo_response}

def send_to_klaviyo(email, name, products):
    """Envoie les infos du client à Klaviyo"""
    url = "https://a.klaviyo.com/api/lists/{list_id}/relationships/profiles/"

    headers = {"Content-Type": "application/json"}
    payload = {
        "api_key": KLAVIYO_API_KEY,
        "profiles": [{
            "email": email,
            "first_name": name.split(" ")[0] if name else "",
            "last_name": name.split(" ")[-1] if name else "",
            "properties": {
                "last_order_products": products
            }
        }]
    }
    response = requests.post(url, json=payload, headers=headers)
    return response.json()

# Lancer l'API sur le bon port pour Railway
if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))  # Utilisation du port défini par Railway
    uvicorn.run(app, host="0.0.0.0", port=port)


