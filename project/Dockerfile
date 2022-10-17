FROM python:3.8
LABEL maintainer="Sai Suhas Kolukula"

# Copy the app to /
COPY techtrends /techtrends
WORKDIR /techtrends

# Install required pip pkgs
RUN pip install -r requirements.txt

# Initialize the SQLite DB
RUN python init_db.py

# Expose default application port
EXPOSE 3111

# Start the TechTrends site on container start
CMD [ "python", "app.py" ]
