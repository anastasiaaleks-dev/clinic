import pickle, sklearn
import pandas as pd
from dateutil import relativedelta

with open('accounts/model_with_scaler.pkl', 'rb') as file:
    model = pickle.load(file)

def calculate_age(appointment):
    start_date = appointment.patient.patient_profile.date_of_birth
    end_date = appointment.appointment_date
    delta = relativedelta.relativedelta(end_date, start_date)
    return delta.years

def calculate_risk(appointment):
    age = calculate_age(appointment)

    condylomatosis = int(appointment.condylomatosis)
    smoking = int(appointment.smoking)
    hormonal_contraception= int(appointment.hormonal_contraception)
    iud = int(appointment.iud)
    hiv = int(appointment.hiv)
    schiller_test = int(appointment.schiller_test)

    input_data = pd.DataFrame(columns=['Age', 'Number of sexual partners', 'First sexual intercourse', 'Num of pregnancies', 'STDs:condylomatosis', 'Smokes', 'Smokes (years)', 'Hormonal Contraceptives', 'Hormonal Contraceptives (years)', 'IUD', 'IUD (years)', 'STDs:HIV', 'Schiller'])
    input_data.loc[0] = [age, appointment.num_of_sexual_partners, appointment.first_sexual_intercourse, condylomatosis, appointment.num_pregnancies, smoking, appointment.smoking_years, hormonal_contraception, appointment.hormonal_years, iud, appointment.iud_years, hiv, schiller_test]

    probabilities = model.predict_proba(input_data)

    risk = round(probabilities[0][1] * 100, 2)

    if risk >= 50:
        risk_class = 'Выше среднего'
    else:
        risk_class = 'Ниже среднего'

    return risk_class, min(risk, 100)
