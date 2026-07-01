from flask import Flask, render_template, request
import joblib
import pandas as pd
import os

app = Flask(__name__)

# Load trained model
try:
    model_path = os.path.join(os.path.dirname(__file__), "model/loan_model.pkl")
    model = joblib.load(model_path)
    print("✅ Model loaded successfully!")
except Exception as e:
    print(f"❌ Error loading model: {e}")
    model = None


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/predict", methods=["POST"])
def predict():
    try:
        # ===============================
        # ORIGINAL INPUTS
        # ===============================
        no_of_dependents = int(request.form.get("no_of_dependents", 0))
        education = request.form.get("education", "")
        self_employed = request.form.get("self_employed", "")
        income_annum = float(request.form.get("income_annum", 0))
        loan_amount = float(request.form.get("loan_amount", 0))
        loan_term = int(request.form.get("loan_term", 0))
        cibil_score = float(request.form.get("cibil_score", 0))
        residential_assets_value = float(request.form.get("residential_assets_value", 0))
        commercial_assets_value = float(request.form.get("commercial_assets_value", 0))
        luxury_assets_value = float(request.form.get("luxury_assets_value", 0))
        bank_asset_value = float(request.form.get("bank_asset_value", 0))

        # ===============================
        # 🔥 NEW CREDIT BEHAVIOR INPUTS
        # ===============================
        missed_payments = int(request.form.get("missed_payments", 0))
        credit_utilization = float(request.form.get("credit_utilization", 0))
        active_loans = int(request.form.get("active_loans", 0))
        credit_history_years = int(request.form.get("credit_history_years", 0))
        credit_inquiries = int(request.form.get("credit_inquiries", 0))

        # ===============================
        # MODEL CHECK
        # ===============================
        if model is None:
            return render_template("index.html", prediction="Model not loaded")

        # ===============================
        # SIMPLE RULE (REALISM FIX)
        # ===============================
        if income_annum == 0 or loan_amount > income_annum * 8:
            result = "Loan Rejected (Unrealistic loan amount)"
        else:
            # Create input for model
            loan_income_ratio = loan_amount / (income_annum + 1)

            input_data = pd.DataFrame([{
                "no_of_dependents": no_of_dependents,
                "education": education,
                "self_employed": self_employed,
                "income_annum": income_annum,
                "loan_amount": loan_amount,
                "loan_term": loan_term,
                "cibil_score": cibil_score,
                "residential_assets_value": residential_assets_value,
                "commercial_assets_value": commercial_assets_value,
                "luxury_assets_value": luxury_assets_value,
                "bank_asset_value": bank_asset_value,
                "loan_income_ratio": loan_income_ratio
            }])

            prediction = model.predict(input_data)[0]

            if prediction == 0:
                result = "Loan Approved"
            else:
                result = "Loan Rejected"

        # ===============================
        # 🔥 CREDIT SCORE IMPROVEMENT LOGIC
        # ===============================
        score = 100
        suggestions = []

        if missed_payments > 0:
            score -= min(missed_payments * 10, 30)
            suggestions.append("Pay EMIs on time")

        if credit_utilization > 30:
            score -= 15
            suggestions.append("Reduce credit usage below 30%")

        if active_loans > 2:
            score -= 10
            suggestions.append("Avoid taking too many loans")

        if credit_history_years < 3:
            score -= 10
            suggestions.append("Maintain longer credit history")

        if credit_inquiries > 2:
            score -= 10
            suggestions.append("Limit loan inquiries")

        if len(suggestions) == 0:
            suggestions.append("Your credit profile is excellent")

        # ===============================
        # FINAL OUTPUT (CLEAN)
        # ===============================
        final_result = f"{result}|Credit Score Health: {score}/100|Suggestions: {', '.join(suggestions)}"

        return render_template("index.html", prediction=final_result)

    except Exception as e:
        return render_template("index.html", prediction=f"Error: {str(e)}")


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=True, host='0.0.0.0', port=port)