#Projede kullanılan kütüphaneler projeye eklendi.

import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, OneHotEncoder, StandardScaler
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import cross_val_score, GridSearchCV
from sklearn.metrics import mean_squared_error, mean_absolute_error

#df değişkenine veri dosyamızı atama işlemi gerçekleştirdik.
df = pd.read_csv('insurance.csv')

#Tablomuzu görmek için ilk 5 satırım
df.head(5)

#BMİ (Vücut kitle indeksi) dağılımını inceleyip grafiğe döküyoruz.
sns.histplot(df['bmi'], kde=True)
plt.xlabel('BMI')
plt.ylabel('frquency')
plt.title('Distribution of BMI')
plt.show()

#Sigara içenlerin ve içmeyenlerin masrafları arasındaki durumu grafiğe döktük.
sns.boxplot(x='smoker', y='charges', data=df)
plt.xlabel('Smoker')
plt.ylabel('Charges')
plt.title('Smoker vs Charges')
plt.show()

#Bölgelere göre sigara içim dağılımını grafiğe döktük
sns.countplot(x='region', hue='smoker', data=df)
plt.xlabel('Region')
plt.ylabel('Count')
plt.title('Region vs Smoker')
plt.legend(title='Smoker', labels=['Non-Smoker', 'Smoker'])
plt.show()

#Kadın ve erkeklerin vücut kitle indekslerinin dağılımını grafiğe döktük
sns.boxplot(x='sex', y='bmi', data=df)
plt.xlabel('Sex')
plt.ylabel('BMI')
plt.title('Sex vs BMI')
plt.xticks([0, 1], ['Male', 'Female'])
plt.show()

#En çok çocucuğun bulunduğu bölgeyi belirttik.
region_with_most_children = df.groupby('region')['children'].sum().idxmax()
print("Region with most children:", region_with_most_children)

#Yaş ve BMİ dağılımını scatterplot kullanarak gösterdik.
sns.scatterplot(x='age', y='bmi', data=df)
plt.xlabel('Age')
plt.ylabel('BMI')
plt.title('Age vs BMI')
plt.show()

#BMİ ve çocuklar arasındaki ilişkiyi kutu grafiğinde inceledik.
sns.boxplot(x='children', y='bmi', data=df)
plt.xlabel('Number of Children')
plt.ylabel('BMI')
plt.title('Children vs BMI')
plt.show()

# "BMI" verilerinde aykırı bir değer olup olmadığını kontrol etme işlemi
Q1 = df['bmi'].quantile(0.25)
Q3 = df['bmi'].quantile(0.75)
IQR = Q3 - Q1

lower_bound = Q1 - 1.5 * IQR
upper_bound = Q3 + 1.5 * IQR

outliers = df[(df['bmi'] < lower_bound) | (df['bmi'] > upper_bound)]

if outliers.empty:
    print("No outliers in the BMI variable.")
else:
    print("Outliers found in the BMI variable.")
    print(outliers[['age', 'sex', 'bmi']])

#Vücut kitle indeksi ve masraflar arasındaki ilişkiyi inceledik.
sns.scatterplot(x='bmi', y='charges', data=df)
plt.xlabel('BMI')
plt.ylabel('Charges')
plt.title('BMI vs Charges')
plt.show()

#BMİ ve bölger arasındaki ilişkileri inceledik
sns.barplot(x='region', y='bmi', hue='smoker', data=df)
plt.xlabel('Region')
plt.ylabel('BMI')
plt.title('Region vs BMI by Smoker')
plt.legend(title='Smoker', labels=['Non-Smoker', 'Smoker'])
plt.show()

label_encoder = LabelEncoder()

# Label Encoding kullanarak kategorik değişkenleri dönüştürme işlemi
df['sex'] = label_encoder.fit_transform(df['sex'])
df['smoker'] = label_encoder.fit_transform(df['smoker'])

# 'region' için One-Hot Encoding kullanımı
onehot_encoder = OneHotEncoder(drop='first', sparse_output=False)
region_encoded = pd.DataFrame(onehot_encoder.fit_transform(df[['region']]))
region_encoded.columns = [f'region_{col}' for col in region_encoded.columns]  # Convert column names to strings
data = pd.concat([df, region_encoded], axis=1)

# 'bölge' sütununu tablodan silme işlemi
data.drop('region', axis=1, inplace=True)

X = data.drop('charges', axis=1)
y = data['charges']  # Hedef değişken

# Verileri eğitim ve test setlerine ayırma işlemi
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

scaler = StandardScaler()

# Eğitim verilerini fit metodu ile öğretme ve dönüştürme işlemi
X_train_scaled = scaler.fit_transform(X_train)

# Test verileri üzerinde dönüştürme işlemi yapma
X_test_scaled = scaler.transform(X_test)

#Regresyon modelleri oluşturma işlemi:

linear_reg = LinearRegression()
rf_reg = RandomForestRegressor()

#scaled training verilerini kullanarak modelleri eğitme işlemi

linear_reg.fit(X_train_scaled, y_train)
rf_reg.fit(X_train_scaled, y_train)

#cross-validation yöntemiyle verilerin performansını değerlendirme işlemi

linear_scores = cross_val_score(linear_reg, X_train_scaled, y_train, cv=5, scoring='neg_mean_squared_error')
rf_scores = cross_val_score(rf_reg, X_train_scaled, y_train, cv=5, scoring='neg_mean_squared_error')

linear_rmse_scores = np.sqrt(-linear_scores)
rf_rmse_scores = np.sqrt(-rf_scores)

print("Linear Regression RMSE Scores:", linear_rmse_scores)
print("Random Forest RMSE Scores:", rf_rmse_scores)

#Bu kod, Doğrusal Regresyon ve Rastgele Orman modellerini önceden işlenmiş veriler üzerinde
#eğitecek ve ardından çapraz doğrulama kullanarak performanslarını değerlendirecektir.
#Hesaplanan RMSE (Kök Ortalama Karesel Hata) puanları, her modelin ne kadar iyi performans
#gösterdiğine dair size bir fikir verecektir.

param_grid = {
    'n_estimators': [100, 200, 300],
    'max_depth': [None, 10, 20],
    'min_samples_split': [2, 5, 10],
    'min_samples_leaf': [1, 2, 4]
}

grid_search = GridSearchCV(rf_reg, param_grid, cv=5, scoring='neg_mean_squared_error', verbose=2)
grid_search.fit(X_train_scaled, y_train)
best_rf_model = grid_search.best_estimator_

#Regresyon modeli değerlendirme ölçümlerini kullanarak optimize edilmiş modeli değerlendirme işlemi
y_pred = best_rf_model.predict(X_test_scaled)
mse = mean_squared_error(y_test, y_pred)
mae = mean_absolute_error(y_test, y_pred)

print("Mean Squared Error:", mse)
print("Mean Absolute Error:", mae)
