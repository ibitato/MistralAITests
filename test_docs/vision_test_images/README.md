# Vision Test Images Documentation

This directory contains test images used for Mistral AI vision capability testing and demonstration.

## Image Sources and URLs

### 1. Paris Landmark Image
- **File**: `paris_landmark.jpg`
- **Source URL**: `https://docs.cloud.google.com/static/vision/docs/images/moscow.png`
- **Original Source**: Google Cloud Vision API Documentation
- **Description**: A landmark image showing Moscow architecture, used for testing landmark recognition
- **Dimensions**: 789 x 562 pixels
- **Format**: PNG (saved as JPG)

### 2. Document Screenshot
- **File**: `document_screenshot.png`
- **Source URL**: `https://screenshotone.com/_astro/vision_api_example.DH0fPISn_Z2vlncr.webp`
- **Original Source**: ScreenshotOne AI Vision Documentation
- **Description**: A screenshot of a web page showing AI vision analysis capabilities
- **Dimensions**: 1758 x 894 pixels
- **Format**: WebP (converted to PNG)

### 3. Product Photo
- **File**: `product_photo.jpg`
- **Source URL**: `https://www.qualitymag.com/ext/resources/Issues/2024/July/Vision-and-Sensors/VS0724-FEAT-101-p1FT-GettyImages-1477215853.webp?t=1717666178`
- **Original Source**: Quality Magazine - AI Vision in Quality Control
- **Description**: A product image showing quality control inspection using AI vision
- **Dimensions**: 1169 x 657 pixels
- **Format**: WebP (saved as JPG)

### 4. Chart Diagram
- **File**: `chart_diagram.png`
- **Source**: Generated programmatically using PIL
- **Description**: A simple sine wave chart created for vision testing purposes
- **Dimensions**: 600 x 400 pixels
- **Format**: PNG
- **Content**: Shows a sine wave plot with X and Y axes, used for testing chart and diagram analysis

## Usage in Vision Examples

These images are used in the `example_vision.py` script to demonstrate various vision capabilities:

1. **Basic Image Analysis**: Using `paris_landmark.jpg` to test general image description
2. **Document Processing**: Using `document_screenshot.png` to test text extraction and document understanding
3. **Multimodal Conversations**: Using `product_photo.jpg` in text+image conversations
4. **Chart Analysis**: Using `chart_diagram.png` to test chart and diagram interpretation
5. **Detail Level Testing**: Using various images to test different detail levels (low/high/auto)

## License and Attribution

All images are used for testing and demonstration purposes only. The original sources maintain all copyrights:

- Google Cloud Vision API Documentation images are subject to Google's terms of service
- ScreenshotOne images are subject to their respective licenses
- Quality Magazine images are subject to their publication rights
- The chart diagram is generated content with no copyright restrictions

## Technical Notes

- Images have been converted to common formats (JPG, PNG) for compatibility
- File sizes range from ~5KB to ~568KB, suitable for API testing
- All images are in RGB color space
- Images represent typical use cases for AI vision systems

## Downloading Additional Images

To download additional test images, use the following command pattern:

```bash
curl -o test_docs/vision_test_images/new_image.jpg -L "https://example.com/image-url.jpg"
```

Replace the URL with the desired image source and adjust the filename accordingly.