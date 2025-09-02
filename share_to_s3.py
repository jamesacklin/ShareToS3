import sublime
import sublime_plugin
import urllib.request
import urllib.parse
import urllib.error
import hashlib
import hmac
from datetime import datetime, timezone
import threading


def aws4_sign_request(method, url, payload, access_key, secret_key, region='global'):
    """Sign a request using AWS Signature Version 4"""
    from urllib.parse import urlparse
    
    parsed_url = urlparse(url)
    host = parsed_url.netloc
    path = parsed_url.path
    
    # Create timestamp
    now = datetime.now(timezone.utc)
    amz_date = now.strftime('%Y%m%dT%H%M%SZ')
    date_stamp = now.strftime('%Y%m%d')
    
    # Create headers
    headers = {
        'Host': host,
        'X-Amz-Date': amz_date,
        'X-Amz-Content-Sha256': hashlib.sha256(payload).hexdigest(),
        'Content-Type': 'text/plain; charset=utf-8'
    }
    
    # Create canonical request
    canonical_headers = ''
    signed_headers = []
    for key in sorted(headers.keys()):
        canonical_headers += key.lower() + ':' + str(headers[key]).strip() + '\n'
        signed_headers.append(key.lower())
    
    signed_headers_str = ';'.join(signed_headers)
    canonical_request = (method + '\n' + 
                        path + '\n' + 
                        '\n' + 
                        canonical_headers + '\n' + 
                        signed_headers_str + '\n' + 
                        headers['X-Amz-Content-Sha256'])
    
    # Create string to sign
    algorithm = 'AWS4-HMAC-SHA256'
    credential_scope = date_stamp + '/' + region + '/s3/aws4_request'
    string_to_sign = (algorithm + '\n' + 
                     amz_date + '\n' + 
                     credential_scope + '\n' + 
                     hashlib.sha256(canonical_request.encode()).hexdigest())
    
    # Calculate signature
    def sign(key, msg):
        return hmac.new(key, msg.encode('utf-8'), hashlib.sha256).digest()
    
    def get_signature_key(key, date_stamp, region_name, service_name):
        k_date = sign(('AWS4' + key).encode('utf-8'), date_stamp)
        k_region = sign(k_date, region_name)
        k_service = sign(k_region, service_name)
        k_signing = sign(k_service, 'aws4_request')
        return k_signing
    
    signing_key = get_signature_key(secret_key, date_stamp, region, 's3')
    signature = hmac.new(signing_key, string_to_sign.encode('utf-8'), hashlib.sha256).hexdigest()
    
    # Create authorization header
    authorization_header = (algorithm + ' ' + 
                           'Credential=' + access_key + '/' + credential_scope + ', ' +
                           'SignedHeaders=' + signed_headers_str + ', ' + 
                           'Signature=' + signature)
    
    headers['Authorization'] = authorization_header
    return headers


def load_settings():
    """Load and validate S3 settings from configuration"""
    settings = sublime.load_settings("ShareToS3.sublime-settings")
    
    endpoint = settings.get("s3_endpoint")
    access_key = settings.get("s3_username")
    secret_key = settings.get("s3_password")
    url_prefix = settings.get("s3_url_prefix")
    bucket = settings.get("s3_bucket", "uploads")
    region = settings.get("s3_region", "global")
    
    if not all([endpoint, access_key, secret_key, url_prefix]):
        sublime.error_message("ShareToS3: Please configure S3 settings in Preferences → Package Settings → ShareToS3 → Settings")
        return None
    
    return {
        'endpoint': endpoint,
        'access_key': access_key,
        'secret_key': secret_key,
        'url_prefix': url_prefix,
        'bucket': bucket,
        'region': region
    }


def validate_content(view):
    """Extract and validate buffer content"""
    content = view.substr(sublime.Region(0, view.size()))
    if not content.strip():
        sublime.error_message("ShareToS3: Buffer is empty")
        return None
    return content


def upload_to_s3_async(content, filename, settings_dict):
    """Upload content to S3 in background thread"""
    def upload_to_s3():
        try:
            data = content.encode('utf-8')
            url = "{}/{}/{}".format(settings_dict['endpoint'].rstrip('/'), settings_dict['bucket'], filename)
            
            headers = aws4_sign_request('PUT', url, data, settings_dict['access_key'], settings_dict['secret_key'], settings_dict['region'])
            
            request = urllib.request.Request(url, data=data, method='PUT')
            for header, value in headers.items():
                request.add_header(header, value)
            
            with urllib.request.urlopen(request, timeout=30) as response:
                if response.getcode() in [200, 201]:
                    public_url = "{}/{}/{}".format(settings_dict['url_prefix'].rstrip('/'), settings_dict['bucket'], filename)
                    sublime.set_clipboard(public_url)
                    sublime.status_message("ShareToS3: Uploaded and copied URL to clipboard")
                else:
                    sublime.error_message("ShareToS3: Upload failed with status {}".format(response.getcode()))
                    
        except urllib.error.HTTPError as e:
            sublime.error_message("ShareToS3: HTTP Error {}: {}".format(e.code, e.reason))
        except urllib.error.URLError as e:
            sublime.error_message("ShareToS3: Connection Error: {}".format(e.reason))
        except Exception as e:
            sublime.error_message("ShareToS3: Error: {}".format(str(e)))
    
    threading.Thread(target=upload_to_s3, daemon=True).start()
    sublime.status_message("ShareToS3: Uploading...")


class ShareToS3Command(sublime_plugin.TextCommand):
    def run(self, edit):
        settings_dict = load_settings()
        if not settings_dict:
            return
        
        content = validate_content(self.view)
        if not content:
            return
        
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        filename = "{}.txt".format(timestamp)
        
        upload_to_s3_async(content, filename, settings_dict)


class ShareToS3WithCustomNameCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        settings_dict = load_settings()
        if not settings_dict:
            return
        
        content = validate_content(self.view)
        if not content:
            return
        
        def on_done(filename):
            if not filename:
                return
            
            if not filename.endswith('.txt'):
                filename += '.txt'
            
            upload_to_s3_async(content, filename, settings_dict)
        
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        self.view.window().show_input_panel("Filename:", "{}.txt".format(timestamp), on_done, None, None)