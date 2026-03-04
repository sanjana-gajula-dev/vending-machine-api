from flask import Flask, request, jsonify, render_template_string

app = Flask(__name__)
items = {
    "A1": {"id": "A1", "name": "Cola", "price_cents": 150, "quantity": 5},
    "B1": {"id": "B1", "name": "Chips", "price_cents": 100, "quantity": 3},
    "C1": {"id": "C1", "name": "Water", "price_cents": 75, "quantity": 10}
}

@app.route("/")
def home():
    return "Vending Machine API is running!"
    
@app.route("/inventory", methods=["GET"])
def get_inventory():
    machine_id = request.headers.get("X-Machine-Id")

    if not machine_id:
        return jsonify({
            "error_code": "MISSING_MACHINE_ID",
            "message": "X-Machine-Id header is required."
        }), 400

    return jsonify(list(items.values())), 200

@app.route("/vend", methods=["POST"])
def vend_item():
    # header
    machine_id = request.headers.get("X-Machine-Id")
    if not machine_id:
        return jsonify({
            "error_code": "MISSING_MACHINE_ID",
            "message": "X-Machine-Id header is required."
        }), 400

    #Get JSON body
    data = request.get_json()

    if not data or "item_id" not in data or "payment_cents" not in data:
        return jsonify({
            "error_code": "INVALID_REQUEST",
            "message": "item_id and payment_cents are required."
        }), 400

    item_id = data["item_id"]
    payment = data["payment_cents"]

    # item exists
    if item_id not in items:
        return jsonify({
            "error_code": "ITEM_NOT_FOUND",
            "message": "The requested item does not exist."
        }), 404

    item = items[item_id]

    #  Check stock
    if item["quantity"] <= 0:
        return jsonify({
            "error_code": "OUT_OF_STOCK",
            "message": "Item is out of stock."
        }), 404

    # Special A1 Rule
    if item_id == "A1" and payment < item["price_cents"]:
        return jsonify({
            "error_code": "A1_BROKE",
            "message": "Legacy hardware malfunction for A1."
        }), 400

    # insufficient funds
    if payment < item["price_cents"]:
        return jsonify({
            "error_code": "INSUFFICIENT_FUNDS",
            "message": "Payment amount is less than the item price."
        }), 400

    # Success case
    item["quantity"] -= 1
    change = payment - item["price_cents"]

    return jsonify({
        "vended_item_id": item_id,
        "change_returned_cents": change
    }), 200


if __name__ == "__main__":
    app.run(port=8000)
