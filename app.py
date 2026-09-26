import os
import pickle
from pathlib import Path

import pandas as pd
from flask import Flask, render_template, request, jsonify
from google import genai
from google.genai import types
from dotenv import load_dotenv

app = Flask(__name__)
BASE_DIR = Path(__file__).resolve().parent


def load_pickle(filename):
    with open(BASE_DIR / filename, 'rb') as file:
        return pickle.load(file)


model = load_pickle('model.pkl')
scaler = load_pickle('scaler.pkl')
robust = load_pickle('robust.pkl')
binary_encoder = load_pickle('label_encoders.pkl')

MODEL_FEATURES = list(model.feature_names_in_)
BINARY_VALUES = {
    str(label): index for index, label in enumerate(binary_encoder.classes_)
}
OBESITY_LABELS = {
    0: 'Insufficient Weight',
    1: 'Normal Weight',
    2: 'Overweight Level I',
    3: 'Overweight Level II',
    4: 'Obesity Type I',
    5: 'Obesity Type II',
    6: 'Obesity Type III',
}
CATEGORY_VALUES = {
    'Gender': {'Female': 0, 'Male': 1},
    'family_history_with_overweight': BINARY_VALUES,
    'FAVC': BINARY_VALUES,
    'CAEC': {'Always': 0, 'Frequently': 1, 'no': 2, 'Sometimes': 3},
    'SMOKE': BINARY_VALUES,
    'SCC': BINARY_VALUES,
    'CALC': {'Always': 0, 'Frequently': 1, 'Sometimes': 2, 'no': 3},
}

HYPERTENSION_MODEL = load_pickle('model_hypertension.pkl')
HYPERTENSION_GENDER = load_pickle('mapping_gender.pkl')
HYPERTENSION_FAMILY_HISTORY = load_pickle('mapping_family_history.pkl')
HYPERTENSION_DIABETES = load_pickle('mapping_diabetes.pkl')
HYPERTENSION_LABELS = load_pickle('mapping_hypertension.pkl')
HYPERTENSION_COLUMNS = list(load_pickle('training_columns.pkl'))
HYPERTENSION_STD_SCALER = load_pickle('std_scaler.pkl')
HYPERTENSION_ORDINAL_SCALER = load_pickle('ordinal_scaler.pkl')
HYPERTENSION_NUMERIC_FIELDS = [
    'Age', 'BMI', 'Cholesterol', 'Systolic_BP', 'Diastolic_BP',
    'Alcohol_Intake', 'Stress_Level', 'Salt_Intake', 'Sleep_Duration',
    'Heart_Rate', 'Glucose',
]

LUNG_MODEL = load_pickle('lung_cancer_model.pkl')
LUNG_SCALER = load_pickle('scaler_lung_cancer.pkl')
LUNG_FEATURES = list(LUNG_MODEL.feature_names_in_)

HEART_MODEL = load_pickle('modelheart.pkl')
HEART_SCALER = load_pickle('scalerheart.pkl')
HEART_ROBUST_SCALER = load_pickle('robusheartt.pkl')
HEART_ENCODERS = load_pickle('label_encodersheart.pkl')
HEART_FEATURES = list(HEART_MODEL.feature_names_in_)
HEART_STAGE_LABELS = {
    0: 'No heart stroke detected',
    1: 'Heart stroke stage 1',
    2: 'Heart stroke stage 2',
    3: 'Heart stroke stage 3',
    4: 'Heart stroke high risk (stage 4)',
}


def predict_obesity(form):
    values = {}
    for feature in MODEL_FEATURES:
        if feature.startswith('MTRANS_'):
            continue

        raw_value = form.get(feature, '').strip()
        if not raw_value:
            raise ValueError('Please complete every field before predicting.')

        if feature in CATEGORY_VALUES:
            if raw_value not in CATEGORY_VALUES[feature]:
                raise ValueError(f'Unsupported value for {feature}.')
            values[feature] = CATEGORY_VALUES[feature][raw_value]
        else:
            try:
                values[feature] = float(raw_value)
            except ValueError as exc:
                raise ValueError(f'{feature} must be a number.') from exc

    transport = form.get('MTRANS', '').strip()
    valid_transport = {
        'Automobile', 'Bike', 'Motorbike', 'Public_Transportation', 'Walking'
    }
    if transport not in valid_transport:
        raise ValueError('Please select a valid transport method.')

    for feature in MODEL_FEATURES:
        if feature.startswith('MTRANS_'):
            values[feature] = float(transport == feature.removeprefix('MTRANS_'))

    row = pd.DataFrame(
        [[values[feature] for feature in MODEL_FEATURES]],
        columns=MODEL_FEATURES,
        dtype=float,
    )
    for transformer in (robust, scaler):
        feature_names = list(getattr(transformer, 'feature_names_in_', []))
        if feature_names:
            indexes = [MODEL_FEATURES.index(feature) for feature in feature_names]
            selected_features = [MODEL_FEATURES[index] for index in indexes]
            row[selected_features] = transformer.transform(row[selected_features])

    prediction = int(model.predict(row)[0])
    bmi = values['Weight'] / (values['Height'] ** 2)
    return {
        'bmi': round(bmi, 1),
        'label': OBESITY_LABELS.get(prediction, str(prediction)),
        'is_obesity': prediction >= 4,
    }


def predict_hypertension(form):
    values = {}
    for field in HYPERTENSION_NUMERIC_FIELDS:
        raw_value = form.get(field, '').strip()
        if not raw_value:
            raise ValueError('Please complete every field before predicting.')
        try:
            values[field] = float(raw_value)
        except ValueError as exc:
            raise ValueError(f'{field} must be a number.') from exc

    physical_activity = form.get('Physical_Activity_Level', '').strip()
    if physical_activity not in {'Low', 'Moderate', 'High'}:
        raise ValueError('Please select a valid physical activity level.')

    gender = form.get('Gender', '').strip()
    family_history = form.get('Family_History', '').strip()
    diabetes = form.get('Diabetes', '').strip()
    smoking = form.get('Smoking_Status', '').strip()
    if gender not in HYPERTENSION_GENDER:
        raise ValueError('Please select a valid gender.')
    if family_history not in HYPERTENSION_FAMILY_HISTORY:
        raise ValueError('Please select a valid family history value.')
    if diabetes not in HYPERTENSION_DIABETES:
        raise ValueError('Please select a valid diabetes value.')
    if smoking not in {'Yes', 'No'}:
        raise ValueError('Please select a valid smoking status.')

    values['Physical_Activity_Level'] = physical_activity
    values['Family_History'] = HYPERTENSION_FAMILY_HISTORY[family_history]
    values['Diabetes'] = HYPERTENSION_DIABETES[diabetes]
    values['Gender'] = HYPERTENSION_GENDER[gender]
    values['Smoking_Status_Former'] = 0
    values['Smoking_Status_Never'] = int(smoking == 'No')

    features = pd.DataFrame([values])
    features['Physical_Activity_Level'] = HYPERTENSION_ORDINAL_SCALER.transform(
        features[['Physical_Activity_Level']]
    ).ravel()
    standardized_fields = list(HYPERTENSION_STD_SCALER.feature_names_in_)
    features[standardized_fields] = HYPERTENSION_STD_SCALER.transform(
        features[standardized_fields]
    )
    features = features[HYPERTENSION_COLUMNS]

    prediction = int(HYPERTENSION_MODEL.predict(features)[0])
    probabilities = HYPERTENSION_MODEL.predict_proba(features)[0]
    level = next(
        label for label, value in HYPERTENSION_LABELS.items()
        if value == prediction
    )
    confidence = round(float(probabilities[prediction]) * 100)
    message = (
        'Several entered indicators suggest elevated risk. Please discuss '
        'these results with a qualified healthcare professional.'
        if level == 'High'
        else 'The entered indicators suggest a lower screening risk. Continue '
        'healthy habits and regular blood pressure checks.'
    )
    return {'level': level, 'score': confidence, 'message': message}


def predict_lung_cancer(form):
    values = {}
    for feature in LUNG_FEATURES:
        raw_value = form.get(feature, '').strip()
        if not raw_value:
            raise ValueError('Please complete every field before predicting.')
        try:
            values[feature] = float(raw_value)
        except ValueError as exc:
            raise ValueError(f'{feature} must be a number.') from exc

    features = pd.DataFrame([values], columns=LUNG_FEATURES, dtype=float)
    scaled_fields = list(LUNG_SCALER.feature_names_in_)
    features[scaled_fields] = LUNG_SCALER.transform(features[scaled_fields])
    prediction = int(LUNG_MODEL.predict(features)[0])

    probability = None
    if hasattr(LUNG_MODEL, 'predict_proba'):
        class_index = list(LUNG_MODEL.classes_).index(1)
        probability = round(float(LUNG_MODEL.predict_proba(features)[0][class_index]) * 100)

    return {
        'is_high_risk': prediction == 1,
        'label': 'High risk of lung cancer' if prediction == 1 else 'Low risk',
        'probability': probability,
    }


def predict_heart_stroke(form):
    numeric_fields = [
        'age', 'trestbps', 'chol', 'thalch', 'oldpeak', 'bmi',
    ]
    values = {}
    for field in numeric_fields:
        raw_value = form.get(field, '').strip()
        if not raw_value:
            raise ValueError('Please complete every field before predicting.')
        try:
            values[field] = float(raw_value)
        except ValueError as exc:
            raise ValueError(f'{field} must be a number.') from exc

    for field in ('smoking_status', 'slope'):
        raw_value = form.get(field, '').strip()
        if not raw_value:
            raise ValueError('Please complete every field before predicting.')
        try:
            values[field] = int(raw_value)
        except ValueError as exc:
            raise ValueError(f'{field} must be a whole number.') from exc

    binary_fields = ('sex', 'fbs', 'exang', 'diabetes', 'family_history')
    for field in binary_fields:
        raw_value = form.get(field, '').strip()
        if raw_value not in {'0', '1'}:
            raise ValueError(f'Please select a valid value for {field}.')
        encoder = HEART_ENCODERS[field]
        values[field] = int(encoder.transform([raw_value == '1'])[0])

    dataset = form.get('dataset', '').strip()
    cp = form.get('cp', '').strip()
    restecg = form.get('restecg', '').strip()
    valid_dataset = {'Cleveland', 'Hungary', 'Switzerland', 'VA Long Beach'}
    valid_cp = {'asymptomatic', 'non-anginal', 'atypical angina', 'typical angina'}
    valid_restecg = {'normal', 'lv hypertrophy', 'st-t abnormality'}
    if dataset not in valid_dataset or cp not in valid_cp or restecg not in valid_restecg:
        raise ValueError('Please select valid categorical values.')

    features = pd.DataFrame(0.0, index=[0], columns=HEART_FEATURES)
    for field, value in values.items():
        features[field] = value
    for category, value in (
        ('dataset', dataset), ('cp', cp), ('restecg', restecg)
    ):
        column = f'{category}_{value}'
        if column in features.columns:
            features[column] = 1.0

    standard_fields = list(HEART_SCALER.feature_names_in_)
    robust_fields = list(HEART_ROBUST_SCALER.feature_names_in_)
    features[standard_fields] = HEART_SCALER.transform(features[standard_fields])
    features[robust_fields] = HEART_ROBUST_SCALER.transform(features[robust_fields])

    prediction = int(HEART_MODEL.predict(features)[0])
    return {
        'label': HEART_STAGE_LABELS.get(prediction, f'Stage {prediction}'),
        'is_high_risk': prediction >= 3,
    }

# Load environment variables from .env file
load_dotenv()

# Configure Gemini API Key
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY environment variable is not set")

# Initialize Gemini client
client = genai.Client(api_key=GEMINI_API_KEY)

# Model configuration
MODEL_ID = "gemini-3.5-flash-lite"

# System prompt config ensuring it only replies to medical and emotional support
SYSTEM_INSTRUCTION = (
    "You are MediPulse AI, a specialized medical and emotional support assistant. "
    "You ONLY answer questions about health, medicine, symptoms, diseases, wellness, and emotional support. "
    "For non-medical questions, politely decline: 'I am your MediPulse Health & Emotional Support Assistant. "
    "I can only assist with medical and health-related questions.'"
)

@app.route('/')
def home():
    return render_template('index.html')


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/privacy')
def privacy():
    return render_template('privacy.html')


@app.route('/terms')
def terms():
    return render_template('terms.html')


@app.route('/health-facts')
def health_facts():
    return render_template('health_facts.html')


@app.route('/virus-defense')
def virus_defense():
    return render_template('virus_defense.html')


@app.route('/obesity-prediction', methods=['GET', 'POST'])
def obesity_prediction():
    result = None
    error = None

    if request.method == 'POST':
        try:
            result = predict_obesity(request.form)
        except (TypeError, ValueError, KeyError) as exc:
            error = str(exc)
        except Exception:
            error = 'The model could not process these values. Check the inputs and try again.'

    return render_template('obesity_prediction.html', result=result, error=error)


@app.route('/hypertension-prediction', methods=['GET', 'POST'])
def hypertension_prediction():
    result = None
    error = None
    if request.method == 'POST':
        try:
            result = predict_hypertension(request.form)
        except (TypeError, ValueError, KeyError) as exc:
            error = str(exc)
        except Exception:
            error = 'The model could not process these values. Check the inputs and try again.'

    return render_template(
        'hypertension_prediction.html', result=result, error=error
    )


@app.route('/lung-cancer-prediction', methods=['GET', 'POST'])
def lung_cancer_prediction():
    result = None
    error = None
    if request.method == 'POST':
        try:
            result = predict_lung_cancer(request.form)
        except (TypeError, ValueError, KeyError) as exc:
            error = str(exc)
        except Exception:
            error = 'The model could not process these values. Check the inputs and try again.'

    return render_template(
        'lung_cancer_prediction.html', result=result, error=error
    )


@app.route('/heart-stroke-prediction', methods=['GET', 'POST'])
def heart_stroke_prediction():
    result = None
    error = None
    if request.method == 'POST':
        try:
            result = predict_heart_stroke(request.form)
        except (TypeError, ValueError, KeyError) as exc:
            error = str(exc)
        except Exception:
            error = 'The model could not process these values. Check the inputs and try again.'

    return render_template(
        'heart_stroke_prediction.html', result=result, error=error
    )


@app.route('/api/chat', methods=['POST'])
def chat():
    """Chat endpoint for medical and emotional questions via Gemini"""
    try:
        data = request.get_json()
        user_message = data.get('message', '').strip()
        
        if not user_message:
            return jsonify({'error': 'Message cannot be empty'}), 400

        # Generate content using the new client format with system instructions
        response = client.models.generate_content(
            model=MODEL_ID,
            contents=user_message,
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_INSTRUCTION,
                temperature=0.4
            )
        )
        
        return jsonify({'reply': response.text})
        
    except Exception as e:
        error_msg = str(e)
        print(f"[ERROR] Chat API: {error_msg}")
        return jsonify({'reply': f"Error: {error_msg}"}), 500


@app.route('/api/analyze-report', methods=['POST'])
def analyze_report():
    """Analyze medical report using multimodal capabilities (Images/PDFs)"""
    try:
        if 'report' not in request.files:
            return jsonify({'error': 'No file uploaded'}), 400
        
        file = request.files['report']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400

        # Read file bytes
        file_bytes = file.read()
        mime_type = file.content_type or 'image/jpeg'
        
        analysis_prompt = (
            "Analyze this medical report. Provide a clear description of what the findings or values mean, "
            "identify potential disease connections or health risks, and suggest safe medical remedies "
            "or lifestyle changes. Always recommend consulting a certified doctor."
        )

        # Pass bytes payload correctly to Gemini SDK as a Part object
        response = client.models.generate_content(
            model=MODEL_ID,
            contents=[
                analysis_prompt,
                types.Part.from_bytes(
                    data=file_bytes,
                    mime_type=mime_type,
                ),
            ],
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_INSTRUCTION,
                temperature=0.4
            )
        )
        
        return jsonify({'analysis': response.text})
        
    except Exception as e:
        error_msg = str(e)
        print(f"[ERROR] Report Analysis: {error_msg}")
        return jsonify({'analysis': f"Error: {error_msg}"}), 500


if __name__ == '__main__':
    app.run(debug=True, port=5000)
