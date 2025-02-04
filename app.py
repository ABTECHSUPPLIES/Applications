import os
from flask import Flask, request, jsonify, render_template
from werkzeug.utils import secure_filename

app = Flask(__name__, template_folder=os.path.join(os.getcwd(), "templates"))

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
    "iPhone XS": {"64GB": 4500, "256GB": 5000, "512GB": 5500},
    "iPhone XS Max": {"64GB": 5000, "256GB": 5500, "512GB": 6000},
    "iPhone XR": {"64GB": 4000, "128GB": 4500, "256GB": 5000},
    "iPhone 11": {"64GB": 6000, "128GB": 6500, "256GB": 7000},
    "iPhone 11 Pro": {"64GB": 8500, "256GB": 9000, "512GB": 9500},
    "iPhone 11 Pro Max": {"64GB": 9000, "256GB": 9500, "512GB": 10000},
    "iPhone SE (2nd Gen)": {"64GB": 5000, "128GB": 5500, "256GB": 6000},
    "iPhone 12": {"64GB": 10000, "128GB": 10500, "256GB": 11000},
    "iPhone 12 Mini": {"64GB": 9000, "128GB": 9500, "256GB": 10000},
    "iPhone 12 Pro": {"128GB": 12000, "256GB": 12500, "512GB": 13000},
    "iPhone 12 Pro Max": {"128GB": 13000, "256GB": 13500, "512GB": 14000},
    "iPhone 13": {"128GB": 11000, "256GB": 11500, "512GB": 12000},
    "iPhone 13 Mini": {"128GB": 10000, "256GB": 10500, "512GB": 11000},
    "iPhone 13 Pro": {"128GB": 13500, "256GB": 14000, "512GB": 14500},
    "iPhone 13 Pro Max": {"128GB": 14500, "256GB": 15000, "512GB": 15500},
    "iPhone 14": {"128GB": 14000, "256GB": 14500, "512GB": 15000},
    "iPhone 14 Plus": {"128GB": 15000, "256GB": 15500, "512GB": 16000},
    "iPhone 14 Pro": {"128GB": 15500, "256GB": 16000, "512GB": 16500},
    "iPhone 14 Pro Max": {"128GB": 16500, "256GB": 17000, "512GB": 17500},
    "iPhone 15": {"128GB": 16000, "256GB": 16500, "512GB": 17000},
    "iPhone 15 Plus": {"128GB": 17000, "256GB": 17500, "512GB": 18000},
    "iPhone 15 Pro": {"128GB": 17500, "256GB": 18000, "512GB": 18500},
    "iPhone 15 Pro Max": {"128GB": 18500, "256GB": 19000, "512GB": 19500},
    "iPhone 16": {"128GB": 18000, "256GB": 18500, "512GB": 19000},
    "iPhone 16 Plus": {"128GB": 19000, "256GB": 19500, "512GB": 20000},
    "iPhone 16 Pro": {"128GB": 19000, "256GB": 19500, "512GB": 20000},
    "iPhone 16 Pro Max": {"128GB": 19500, "256GB": 20000, "512GB": 20500},
}

# Available Colors
IPHONE_COLORS = ["Silver", "Graphite", "Gold", "Blue", "Green", "Black"]

# Interest Rates Based on Repayment Period
INTEREST_RATES = {3: 0.05, 6: 0.08, 12: 0.12, 24: 0.15}

@app.route('/')
def home():
    iphone_details = []
    
    # Preparing structured data for template rendering
    for model, storage_options in IPHONE_PRICES.items():
        iphone_details.append({
            "model": model,
            "storage_options": [
                {"size": storage, "price": price} for storage, price in storage_options.items()
            ],
            "colors": IPHONE_COLORS
        })
    
    return render_template("index.html", iphone_details=iphone_details)

@app.route('/calculate_installment', methods=['POST'])
def calculate_installment():
    data = request.json
    model = data.get("model")
    storage = data.get("storage")
    color = data.get("color")
    deposit = float(data.get("deposit", 750))
    months = int(data.get("months"))

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
