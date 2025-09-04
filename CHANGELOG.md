# 📑 Changelog

All notable changes to this project will be documented in this file.  
This project follows [Semantic Versioning](https://semver.org/).

---

## [Unreleased]
- Add user profile picture upload
- Improve OTP delivery logging
- Add password-based login option

---

## [0.2.0] - 2025-09-03
### Added
- Post creation with text and optional image
- Like/unlike functionality with unique constraints
- SQLite `posts` and `likes` tables

### Changed
- OTP expiry set to 30 seconds
- Improved session handling to store `user_id`

---

## [0.1.0] - 2025-09-01
### Added
- User registration via email
- OTP-based login with AWS SES SMTP
- SQLite `users` table with OTP storage
- Basic Flask app structure with templates