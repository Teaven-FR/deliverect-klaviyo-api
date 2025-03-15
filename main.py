from fastapi import FastAPI, Request
import requests
import os
import uvicorn

app = FastAPI()

# Récupération des variables d'environnement pour Klaviyo
KLAVIYO_API_KEY = os.getenv("KLAVIYO_API_KEY")
KLAVIYO_LIST_ID = os.getenv("KLAVIYO_LIST_ID")

@app.post("/webhook/deliverect/validate/")
async def validate_order(request: Request):
    """Validation des commandes envoyées par Deliverect"""
    order_data = await request.json()
    print("✅ Validation de la commande reçue :", order_data)
    return {"status": "success", "message": "Commande validée"}

@app.post("/webhook/deliverect/")
async def receive_deliverect_order(request: Request):
    """Réception des commandes de Deliverect et envoi des infos à Klaviyo"""
    try:
        order_data = await request.json()
        print("🚀 Commande reçue de Deliverect :", order_data)  # ✅ Debugging

        # Extraction des infos du client
        customer_email = order_data.get("customer", {}).get("email", "")
        customer_name = order_data.get("customer", {}).get("name", "")
        customer_phone = order_data.get("customer", {}).get("phone", "")  # ✅ Ajout du téléphone
        products = [item["name"] for item in order_data.get("orderItems", [])]

        if not customer_email:
            print("⚠️ Aucune adresse email trouvée dans la commande")
            return {"status": "error", "message": "Pas d'email client fourni"}

        # Envoi des informations à Klaviyo
        klaviyo_response = send_to_klaviyo(customer_email, customer_name, customer_phone, products)
        
        print("📩 Réponse de Klaviyo :", klaviyo_response)
        return {"status": "success", "klaviyo_response": klaviyo_response}
    
    except Exception as e:
        print("❌ Erreur lors du traitement de la commande :", str(e))
        return {"status": "error", "message": str(e)}

@app.post("/webhook/deliverect/cancel/")
async def cancel_order(request: Request):
    """Annulation des commandes via Deliverect"""
    order_data = await request.json()
    print("🛑 Commande annulée :", order_data)
    return {"status": "success", "message": "Commande annulée"}

def send_to_klaviyo(email, name, phone, products):
    """Envoie les informations du client à Klaviyo"""
    url = "https://a.klaviyo.com/api/profiles/"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Klaviyo-API-Key {KLAVIYO_API_KEY}"
    }

    payload = {
        "data": {
            "type": "profile",
            "attributes": {
                "email": email,
                "first_name": name.split(" ")[0] if name else "",
                "last_name": name.split(" ")[-1] if name else "",
                "phone_number": phone,  # ✅ Ajout du téléphone
                "properties": {
                    "last_order_products": products
                }
            }
        }
    }

    print("📤 Envoi des données à Klaviyo :", payload)  # ✅ Debugging

    response = requests.post(url, json=payload, headers=headers)

    if response.status_code == 201:
        print("✅ Profil ajouté avec succès dans Klaviyo")
    else:
        print(f"⚠️ Erreur lors de l'envoi à Klaviyo: {response.status_code}, {response.text}")

    return response.json()

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))  # Utilisation du port défini par Railway
    uvicorn.run(app, host="0.0.0.0", port=port)


