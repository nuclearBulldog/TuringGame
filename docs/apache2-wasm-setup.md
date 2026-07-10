# Deploying TuringGame to Apache2 (EC2)

## 1. Build the web bundle

From the project root on your local machine:

```bash
pip install pygbag~=0.9.0
python -m pygbag turing-game/main_web.py
```

pygbag starts a local dev server and writes the static build to `build/web/`.
Once the terminal shows the build is complete, Ctrl-C to stop the server.

## 2. Copy files to the EC2 instance

```bash
scp -r build/web/ ec2-user@<your-ec2-ip>:/var/www/html/turinggame/
```

Replace `ec2-user` and the IP with your actual SSH user and instance address.

## 3. Configure Apache2

### Add the WebAssembly MIME type

Without this, browsers refuse to run the `.wasm` file.

Create a conf snippet:

```apache
# /etc/apache2/conf-available/wasm.conf
AddType application/wasm .wasm
```

Enable and reload:

```bash
sudo a2enconf wasm
sudo systemctl reload apache2
```

### Enable cross-origin isolation headers (required for SharedArrayBuffer)

pygbag requires `SharedArrayBuffer`, which browsers only allow under cross-origin
isolation. Add these headers to your VirtualHost or `.htaccess`:

```apache
Header set Cross-Origin-Opener-Policy "same-origin"
Header set Cross-Origin-Embedder-Policy "require-corp"
```

Enable `mod_headers` if not already on:

```bash
sudo a2enmod headers
sudo systemctl reload apache2
```

### Example VirtualHost snippet

```apache
<VirtualHost *:80>
    ServerName yourdomain.com
    DocumentRoot /var/www/html

    <Directory /var/www/html/turinggame>
        Options Indexes FollowSymLinks
        AllowOverride None
        Require all granted

        Header set Cross-Origin-Opener-Policy "same-origin"
        Header set Cross-Origin-Embedder-Policy "require-corp"
    </Directory>
</VirtualHost>
```

## 4. Verify

Open `http://<your-ec2-ip>/turinggame/index.html` in a browser.
Check DevTools Console — there should be no MIME type or CORS errors.

## Known Limitations

- **Audio:** WASM has limited support for `.wav` and `.mid` files. If music does
  not play in the browser, convert `assets/main-theme.wav` and
  `assets/battle.mid` to `.ogg` and update the paths in `settings.py`.
- **pygame-menu:** some features may behave differently under WASM due to
  threading constraints. Test the main menu thoroughly after deploying.
