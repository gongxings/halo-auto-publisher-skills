# Halo API Notes

This skill targets Halo 2.x console-style APIs. Endpoint defaults:

1. Upload: `/apis/api.console.halo.run/v1alpha1/attachments/upload`
2. Post create: `/apis/api.console.halo.run/v1alpha1/posts`

## Auth

Send:

1. `Authorization: Bearer <HALO_TOKEN>`
2. `Accept: application/json`

## Compatibility

Halo deployments may differ by plugin/version. If post creation fails:

1. Verify endpoint path in your Halo instance.
2. Adjust payload mapping in `scripts/halo_client.ps1`.
3. Keep upload and post logic separate so you can validate each call independently.
