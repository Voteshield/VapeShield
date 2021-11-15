# VapeShield 🌬️ 🛡️

VapeShield is a very simple tool to perform smoke testing for deployed VoteShield API backends. 

<img src="https://raw.githubusercontent.com/Voteshield/VapeShield/feature/vapeshield_art/docs/vape_shield.png" alt="VapeShield" title="Image credit @approtis" width="400"/>

## What exactly does this do?

This is a very simple Github Action that runs whenever there is a change in the API, or in the VoteShield infrastructure. It utilizes the excellent [schemathesis](https://github.com/schemathesis/schemathesis) to grab the OAS3 specfile and tests API responses accordingly. This workflow is essentially a wrapper for Schemathesis, and you specify what to point it to.

## Usage

For a simple example, take a peek at the [self-test](https://github.com/Voteshield/VapeShield/blob/main/.github/workflows/self-test.yaml) workflow in this repository. For example:

```yaml
jobs:
  test-deployment:
    runs-on: ubuntu-20.04
    steps:
      - name: Test a VS deployment
        uses: Voteshield/VapeShield@main
        env:
          VS_API_KEY: ${{ secrets.VS_API_KEY }}
          BASE_URL_ARG: ${{ secrets.BASE_URL_ARG }}
          ENVIRONMENT_ARG: ${{ secrets.ENVIRONMENT_ARG }}
          RETRY_ATTEMPTS: 60
          RETRY_TIMEOUT: 5
```

This action takes three arguments as environmental variables:

- *VS_API_KEY:* Your VoteShield API information. This includes all the details needed to authenticate with your API key.
- *BASE_URL_ARG:* The base URL for the deployed VoteShield environment. For example, api.voteshield.us
- *ENVIRONMENT_ARG:* The environment you are authenticating against. For example, `voteshield`.
- *RETRY_ATTEMPTS:* Optional. The action will try this number of times every second by default to see if the service is available, considering most instances of this being ran will assume a service was cycled somewhere.
- *RETRY_TIMEOUT:* Optional. Set's the timeout in seconds between retries. Defaults to 2 seconds.

## Testing

Testing is pretty straightforward, all you really need is:

```sh
docker build -t VapeShield .
docker run VapeShield --env-file .secrets
```

With your prepared [environment file](https://docs.docker.com/compose/environment-variables/#the-env-file).

## Current Limitations/Future State Items

This list should be updated as time goes on. But, as it stands, some things need to be addressed:

- In its current state, this only hits `GET` routes.
- In order to perform the other CUD operations, we still need to implement [OAS3 links](https://swagger.io/docs/specification/links/) in order to safely modify data.
- This only tests endpoints with example requests. 
- The script hard codes "slow" routes. Ideally, there is a way to do this in the Spec file and we don't have to put them in this.
- Lastly, a lot of these tests fail the first time they are ran. This is because they take a _long_ time to complete, and on the second run the results are cahced. Ideally there is a "seed" function to build out the cache and gracefully fail, or we can identify non-cached responses somehow. 

## Contributing

See [docs/CONTRIBUTING.md](./docs/CONTRIBUTING.md).

## License

Licensed under the [LGPL 3.0](https://www.gnu.org/licenses/lgpl-3.0.en.html); see [LICENSE.txt](./LICENSE.txt) for details.
