import uvicorn

if __name__ == "__main__":
    # This allows you to run the app from the root directory 
    # while pointing to the nested main.py
    uvicorn.run("app.api.main:app", host="127.0.0.1", port=8000, reload=True)