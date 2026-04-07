p_cloudy = 0.40
p_rain = 0.20
p_cloudy_rain = 0.85
result = (p_rain * p_cloudy_rain) / p_cloudy 
print("Probability of rain if it is cloudy:", result) 
print("Percentage:", result * 100, "%")