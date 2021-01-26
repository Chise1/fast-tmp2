from src.factory import create_app
app=create_app()


if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app,debug=True, lifespan="on" )
