# TradeLog

TradeLog is a modern SaaS web application for traders to log, review, and improve their trading performance. Built with Flask, it offers a secure, user-friendly platform for managing trade journals, analyzing performance, and upgrading to premium features.

## Features

- **User Authentication:** Secure registration, login, and logout using Flask-Login and Flask-Bcrypt.
- **Trade Logging:** Add, edit (inline), and delete trades with detailed fields (stock, date & time, bias, position size, entry/exit reason, outcome, R:R, notes, emotion, trading plan, balance, PNL).
- **Free & Premium Tiers:** Free users can log up to 10 trades; premium users have unlimited access.
- **Premium Upgrade:** Integrated payment gateway (Cashfree) for seamless premium upgrades.
- **CSV Export:** Premium users can export their trades as CSV files.
- **Admin Panel:** Manage users and view all registered accounts.
- **Custom Error Pages:** Friendly 403, 404, and 500 error pages.
- **Responsive UI:** Clean, modern design using Tailwind CSS.
- **Blueprint Architecture:** Modular codebase with blueprints for main, auth, trading, and errors.
- **Database:** SQLAlchemy ORM with SQLite (default).
- **Deployment Ready:** Easily deployable on Render.com or any WSGI-compatible host.

## Screenshots

> _Add screenshots of the landing page, dashboard, trade form, and error pages here._

## Getting Started

### Prerequisites
- Python 3.8+
- pip

### Installation
1. **Clone the repository:**
   ```bash
   git clone https://github.com/your-username/tradelog.git
   cd tradelog
   ```
2. **Create a virtual environment:**
   ```bash
   python -m venv myenv
   source myenv/bin/activate  # On Windows: myenv\Scripts\activate
   ```
3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
4. **Set environment variables:**
   - `SECRET_KEY`: Flask secret key
   - `CLIENT_ID`, `CLIENT_SECRET`: Cashfree API credentials
   - (Optional) `DATABASE_URL` for production

5. **Run the app locally:**
   ```bash
   python run.py
   ```
   Visit [http://localhost:5000](http://localhost:5000)

### Deployment (Render.com)
- Set the start command to:
  ```
  gunicorn run:app
  ```
- Add environment variables in the Render dashboard.

## Project Structure
```
tradelog/
  ├── auth/
  ├── errors/
  ├── main/
  ├── trading/
  ├── templates/
  ├── static/
  ├── models.py
  ├── extensions.py
  ├── config.py
  ├── __init__.py
run.py
requirements.txt
```

## Configuration
- All configuration is managed in `tradelog/config.py`.
- Use environment variables for sensitive data.

## Usage
- Register a new account or log in.
- Add, edit, or delete trades from your dashboard.
- Upgrade to premium for unlimited trades and CSV export.
- Admins can manage users from the admin panel.

## Contributing
Pull requests are welcome! For major changes, please open an issue first to discuss what you would like to change.


## Author
- Aqeel Sheikh ([@aqeel-sheikh](https://github.com/aqeel-sheikh))
- Email: sheikhakeelw01@gmail.com

## License
[MIT](LICENSE)

---
_TradeLog – Your personal trading companion._
