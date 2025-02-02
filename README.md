# flickr_downloader

**Flickr Downloader** is a simple and efficient tool designed to help you download your Flickr photos, especially from albums that exceed 500 photos. Flickr's native download process requires splitting larger albums into smaller ones, which can be tedious and time-consuming. This tool eliminates that limitation, enabling seamless downloading of entire albums regardless of size.

## Features
- **Download Large Albums**: Easily download Flickr albums containing more than 500 photos without manual splitting.
- **Preserve Metadata**: Extracts EXIF metadata from each photo and embeds it into the downloaded files, ensuring that important information like timestamps, camera settings, and geolocation is retained.
- **User-Friendly**: Straightforward setup and usage instructions.
- **API Key Integration**: Powered by Flickr's API for secure and reliable access to your photos.

## Getting Started
To use Flickr Downloader, you'll need a Flickr API key. Follow these steps to get started:

1. Go to the [Flickr API Key page](https://www.flickr.com/services/apps/create/apply) and create an app to obtain your API key.
2. Clone this repository to your local machine.
3. Follow the setup and usage instructions provided in the documentation.

## How It Works
1. The tool connects to your Flickr account using your API key.
2. It downloads the photos from your selected albums, bypassing Flickr's limitation on albums with more than 500 photos.
3. It extracts EXIF metadata from each photo and embeds it directly into the downloaded files.
