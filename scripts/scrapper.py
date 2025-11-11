"""
Instagram Post Scraper
Extracts caption and images from Instagram posts without authentication.

Requirements:
    pip install requests beautifulsoup4 lxml

Usage:
    python instagram_scraper.py <post_url>
    
Example:
    python instagram_scraper.py https://www.instagram.com/p/ABC123/
"""

import argparse
import json
import re
import sys
from pathlib import Path
from urllib.parse import urlparse
import requests
from bs4 import BeautifulSoup


class InstagramScraper:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        })

    def extract_post_data(self, url):
        """
        Extract post data from Instagram URL.
        Returns dict with caption and image URLs.
        """
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'lxml')
            
            # Find JSON data embedded in script tags
            scripts = soup.find_all('script', type='application/ld+json')
            post_data = None
            
            for script in scripts:
                try:
                    data = json.loads(script.string)
                    if isinstance(data, dict) and '@type' in data:
                        post_data = data
                        break
                except json.JSONDecodeError:
                    continue
            
            if not post_data:
                # Try to find data in the shared data script
                shared_data_script = soup.find('script', text=re.compile('window._sharedData'))
                if shared_data_script:
                    match = re.search(r'window\._sharedData = ({.*?});', shared_data_script.string)
                    if match:
                        shared_data = json.loads(match.group(1))
                        post_data = self._extract_from_shared_data(shared_data)
            
            if post_data:
                return self._parse_post_data(post_data)
            else:
                return self._fallback_extraction(soup)
                
        except requests.exceptions.RequestException as e:
            print(f"Error fetching URL: {e}", file=sys.stderr)
            return None
        except Exception as e:
            print(f"Error parsing data: {e}", file=sys.stderr)
            return None

    def _extract_from_shared_data(self, shared_data):
        """Extract post data from window._sharedData object."""
        try:
            entry_data = shared_data.get('entry_data', {})
            post_page = entry_data.get('PostPage', [{}])[0]
            media = post_page.get('graphql', {}).get('shortcode_media', {})
            
            return {
                'caption': media.get('edge_media_to_caption', {}).get('edges', [{}])[0].get('node', {}).get('text', ''),
                'image': media.get('display_url', ''),
                'images': [media.get('display_url', '')],
                'is_video': media.get('is_video', False)
            }
        except (KeyError, IndexError):
            return None

    def _parse_post_data(self, data):
        """Parse post data from JSON-LD or shared data."""
        result = {
            'caption': '',
            'images': [],
            'is_video': False
        }
        
        # Extract caption
        if 'caption' in data:
            result['caption'] = data['caption']
        elif 'articleBody' in data:
            result['caption'] = data['articleBody']
        elif 'description' in data:
            result['caption'] = data['description']
        
        # Extract images
        if 'image' in data:
            if isinstance(data['image'], str):
                result['images'] = [data['image']]
            elif isinstance(data['image'], list):
                result['images'] = data['image']
        
        # Check for video
        if 'video' in data or data.get('@type') == 'VideoObject':
            result['is_video'] = True
        
        return result

    def _fallback_extraction(self, soup):
        """Fallback method using meta tags."""
        result = {
            'caption': '',
            'images': [],
            'is_video': False
        }
        
        # Try to get caption from meta description
        meta_desc = soup.find('meta', property='og:description')
        if meta_desc:
            result['caption'] = meta_desc.get('content', '')
        
        # Try to get image from og:image
        meta_image = soup.find('meta', property='og:image')
        if meta_image:
            result['images'] = [meta_image.get('content', '')]
        
        # Check for video
        meta_type = soup.find('meta', property='og:type')
        if meta_type and 'video' in meta_type.get('content', '').lower():
            result['is_video'] = True
        
        return result

    def download_image(self, url, output_dir='downloads'):
        """Download image from URL."""
        try:
            Path(output_dir).mkdir(exist_ok=True)
            
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            # Generate filename from URL
            parsed = urlparse(url)
            filename = Path(parsed.path).name
            if not filename:
                filename = 'image.jpg'
            
            filepath = Path(output_dir) / filename
            
            with open(filepath, 'wb') as f:
                f.write(response.content)
            
            print(f"Downloaded: {filepath}")
            return str(filepath)
            
        except Exception as e:
            print(f"Error downloading image: {e}", file=sys.stderr)
            return None


def main():
    parser = argparse.ArgumentParser(description='Scrape Instagram posts')
    parser.add_argument('url', help='Instagram post URL')
    parser.add_argument('-d', '--download', action='store_true', 
                       help='Download images to local directory')
    parser.add_argument('-o', '--output-dir', default='downloads',
                       help='Output directory for downloaded images')
    parser.add_argument('-j', '--json', action='store_true',
                       help='Output in JSON format')
    
    args = parser.parse_args()
    
    scraper = InstagramScraper()
    
    print(f"Scraping: {args.url}")
    data = scraper.extract_post_data(args.url)
    
    if not data:
        print("Failed to extract post data", file=sys.stderr)
        sys.exit(1)
    
    if args.json:
        print(json.dumps(data, indent=2))
    else:
        print("\n" + "="*60)
        print("CAPTION:")
        print("="*60)
        print(data.get('caption', 'No caption found'))
        print("\n" + "="*60)
        print("IMAGES:")
        print("="*60)
        if data.get('images'):
            for i, img_url in enumerate(data['images'], 1):
                print(f"{i}. {img_url}")
        else:
            print("No images found")
        
        if data.get('is_video'):
            print("\n[NOTE: This is a video post]")
    
    if args.download and data.get('images'):
        print("\nDownloading images...")
        for img_url in data['images']:
            scraper.download_image(img_url, args.output_dir)


if __name__ == '__main__':
    main()