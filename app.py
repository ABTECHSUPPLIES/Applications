import os
from flask import Flask, request, jsonify, render_template
from werkzeug.utils import secure_filename

app = Flask(__name__, template_folder="templates")

print("Templates Path:", os.path.abspath("templates"))
print("Files in Templates:", os.listdir("templates"))


# Upload Folder Configuration
UPLOAD_FOLDER = "uploads"
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "pdf", "doc", "docx"}
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

# iPhone Models, Storage Options, and Prices
IPHONE_PRICES = {
    "iPhone 13 Pro": {"128GB": 13500, "256GB": 14000, "512GB": 14500},
    "iPhone 14 Pro": {"128GB": 15500, "256GB": 16000, "512GB": 16500},
    "iPhone 16 Pro Max": {"128GB": 19500, "256GB": 20000, "512GB": 20500}
}

# Available Colors
IPHONE_COLORS = ["Silver", "Graphite", "Gold", "Blue", "Green", "Black"]

# Interest Rates Based on Repayment Period
INTEREST_RATES = {
    3: 0.05,   # 5%
    6: 0.08,   # 8%
    12: 0.12,  # 12%
    24: 0.15   # 15%
}

@app.route('/')
def home():
    return render_template("index.html", models=IPHONE_PRICES.keys(), colors=IPHONE_COLORS)

@app.route('/calculate_installment', methods=['POST'])
def calculate_installment():
    data = request.json
    model = data.get("model")
    storage = data.get("storage")  # Ensure storage is selected
    color = data.get("color")  # Get selected color
    deposit = float(data.get("deposit", 750))
    months = int(data.get("months"))

    # Validate user inputs
    if model not in IPHONE_PRICES:
        return jsonify({"error": "Invalid iPhone model"}), 400
    if storage not in IPHONE_PRICES[model]:
        return jsonify({"error": "Invalid storage option"}), 400
    if color not in IPHONE_COLORS:
        return jsonify({"error": "Invalid color option"}), 400
    if months not in INTEREST_RATES:
        return jsonify({"error": "Invalid repayment period"}), 400
    if deposit < 750:
        return jsonify({"error": "Deposit must be at least R750"}), 400

    # Calculate Installment
    price = IPHONE_PRICES[model][storage]
    interest_rate = INTEREST_RATES[months]
    amount_financed = price - deposit
    total_payable = amount_financed * (1 + interest_rate)
    monthly_payment = total_payable / months

    return jsonify({
        "model": model,
        "storage": storage,
        "color": color,
        "price": price,
        "deposit": deposit,
        "months": months,
        "interest_rate": f"{interest_rate * 100}%",
        "total_payable": round(total_payable, 2),
        "monthly_payment": round(monthly_payment, 2)
    })

# Upload Proof of Payment (EFT)
@app.route('/upload_proof_payment', methods=['POST'])
def upload_proof_payment():
    if "proof_payment" not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files["proof_payment"]
    if file.filename == "":
        return jsonify({"error": "No selected file"}), 400

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))
        return jsonify({"message": "Proof of Payment Submitted Successfully!"})

    return jsonify({"error": "Invalid file format"}), 400

# Upload Cash Send Proof
@app.route('/upload_cash_send_proof', methods=['POST'])
def upload_cash_send_proof():
    if "cash_send_proof" not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files["cash_send_proof"]
    if file.filename == "":
        return jsonify({"error": "No selected file"}), 400

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))
        return jsonify({"message": "Cash Send Proof Approved!"})

    return jsonify({"error": "Invalid file format"}), 400

# Upload Eligibility Documents
@app.route('/upload_documents', methods=['POST'])
def upload_documents():
    required_files = ["proof_income", "valid_id", "proof_residence"]
    uploaded_files = {}

    for key in required_files:
        file = request.files.get(key)
        if not file:
            return jsonify({"error": f"Missing file: {key}"}), 400
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
            file.save(file_path)
            uploaded_files[key] = filename
        else:
            return jsonify({"error": f"Invalid file format for {key}"}), 400

    return jsonify({"message": "Documents uploaded successfully!"})

if __name__ == '__main__':
    app.run()
