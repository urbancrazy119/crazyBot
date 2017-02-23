import funcWeather as weather
import funcBot as f

msg = weather.make_weather_msg('all')
f.broadcast(msg)
