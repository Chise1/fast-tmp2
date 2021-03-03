from fast_t.factory import create_app
import os
os.environ.setdefault("FASTAPI_SETTINGS_MODULE",'fast_t.settings')
app = create_app()

if __name__ == '__main__':
    import uvicorn

    uvicorn.run(app, debug=True, port=8001, lifespan="on")
