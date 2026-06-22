from fastapi import FastAPI, Request



app=    FastAPI()

@app.get('/')
async def get_root():
    return {'message':'hello world'}