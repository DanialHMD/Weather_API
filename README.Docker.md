### Building and running your application

Start your application:
```sh
docker compose up --build
```
Your application will be available at [http://localhost:8000](http://localhost:8000).

To stop your application, press Ctrl+C or run:
```sh
docker compose down
```

### Environment Variables

If your app uses environment variables, create a `.env` file in the project root.  
Example:
```
API_KEY=your_api_key
DEBUG=1
```

### Deploying your application to the cloud

Build your image:
```sh
docker build -t myapp .
```
For a specific platform (e.g., Mac M1 to amd64):
```sh
docker build --platform=linux/amd64 -t myapp .
```
Push to your registry:
```sh
docker push myregistry.com/myapp
```

Consult Docker's [getting started](https://docs.docker.com/go/get-started-sharing/) docs for more detail.

### References
* [Docker's Python guide](https://docs.docker.com/language/python/)