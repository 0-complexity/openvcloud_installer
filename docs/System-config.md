# System config

The config is needed for the installer to perform its various operations and setup the various componenets of the environment.

## Support

This section is used by the Teleport application to configure the access to the application.
To access the Teleport application you need to have a github oauth application which is defined in the `github` section as follows:

```yaml
support:
  github:
    client_id: 3216584165816f5v
    client_secret: 3wa651wvefqeffefefsf6514651eswrfgw
    teams:
    - team_name: support_beg84
      org_name: be-g8-4
```

To create a github oauth application follow the [docs](https://developer.github.com/apps/building-oauth-apps/creating-an-oauth-app/).
After creating the application you can get both the `client_id` and the `client_secret` from the application page.

Under the `teams` section it is possible to restrict the access to users belonging to a specific github organization as well as specify a specific team that belongs to this organization.
