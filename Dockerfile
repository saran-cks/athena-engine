FROM python:3.14-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install uv
RUN uv pip install --system -r requirements.txt
COPY . .
EXPOSE 8051
CMD ["streamlit", "run", "interface/streamlit_app.py"]
