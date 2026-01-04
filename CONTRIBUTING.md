# Contributing to Interview Preparation Platform

We welcome contributions from the community! This document provides guidelines and information for contributors.

## 🤝 How to Contribute

### Reporting Issues

1. **Bug Reports**

   - Use GitHub Issues with the "Bug" label
   - Provide detailed steps to reproduce
   - Include environment details (OS, Python version, etc.)
   - Add relevant logs or screenshots

2. **Feature Requests**
   - Use GitHub Issues with the "Enhancement" label
   - Describe the feature and its use case
   - Explain why it would be valuable
   - Consider implementation complexity

### Development Setup

1. **Fork and Clone**

```bash
git clone https://github.com/your-username/interview_prep_platform.git
cd interview_prep_platform
```

2. **Set Up Development Environment**

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

3. **Configure Environment**

```bash
cp .env.example .env
# Edit .env with your configuration
```

4. **Run Tests**

```bash
pytest
```

### Making Changes

1. **Create Branch**

```bash
git checkout -b feature/your-feature-name
# or
git checkout -b fix/your-bug-fix
```

2. **Make Changes**

- Follow the existing code style
- Add tests for new functionality
- Update documentation as needed

3. **Run Tests**

```bash
pytest
pytest --cov=src
```

4. **Commit Changes**

```bash
git add .
git commit -m "feat: add your feature description"
# Use conventional commits:
# feat: new feature
# fix: bug fix
# docs: documentation
# style: formatting
# refactor: code refactoring
# test: tests
# chore: maintenance
```

5. **Push and Create PR**

```bash
git push origin feature/your-feature-name
# Create Pull Request on GitHub
```

## 📝 Code Style Guidelines

### Python Style

- Follow PEP 8
- Use type hints for all functions
- Maximum line length: 88 characters
- Use f-strings for string formatting

### Documentation

- Add docstrings to all public functions and classes
- Use Google-style docstrings
- Include parameter types and return types

```python
def create_user(user_data: Dict[str, Any]) -> Dict[str, Any]:
    """Create a new user in the database.

    Args:
        user_data: Dictionary containing user information including
            email, first_name, last_name, and optional profile data.

    Returns:
        Dictionary containing the created user's ID and basic information.

    Raises:
        HTTPException: If user creation fails due to database errors.
    """
```

### Database Queries

- Use parameterized queries to prevent SQL injection
- Add comments for complex queries
- Handle database connections properly with try/finally

```python
try:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
    result = cursor.fetchone()
finally:
    cursor.close()
    conn.close()
```

## 🧪 Testing Guidelines

### Unit Tests

- Write tests for all new functions
- Use pytest fixtures for setup
- Mock external dependencies
- Aim for >80% code coverage

### Test Structure

```
tests/
├── unit/                   # Unit tests
│   ├── test_users.py
│   ├── test_skills.py
│   └── test_assessments.py
├── integration/           # Integration tests
│   ├── test_api.py
│   └── test_database.py
└── conftest.py            # pytest configuration
```

### Test Examples

```python
def test_create_user_success():
    """Test successful user creation."""
    user_data = {
        "email": "test@example.com",
        "first_name": "Test",
        "last_name": "User"
    }

    result = create_user(user_data)

    assert result["message"] == "User created successfully"
    assert "user_id" in result
    assert result["email"] == user_data["email"]
```

## 🏗️ Architecture Guidelines

### Clean Architecture

- Keep business logic in the domain layer
- Use dependency injection
- Separate concerns properly
- Test business logic independently

### API Design

- Use RESTful principles
- Provide meaningful error messages
- Use appropriate HTTP status codes
- Include request/response examples in documentation

### Database Design

- Use meaningful table and column names
- Add appropriate indexes
- Use foreign key constraints
- Include created_at/updated_at timestamps

## 📋 Review Process

### Pull Request Requirements

1. **Description**: Clear description of changes
2. **Testing**: All tests pass
3. **Documentation**: Updated if needed
4. **Code Style**: Follows project guidelines
5. **No Breaking Changes**: Unless necessary

### Review Checklist

- [ ] Code follows style guidelines
- [ ] Tests are included and passing
- [ ] Documentation is updated
- [ ] No sensitive data in code
- [ ] Error handling is appropriate
- [ ] Database queries are safe
- [ ] API endpoints are documented

## 🚀 Deployment

### Development Deployment

1. Create feature branch
2. Make changes
3. Test thoroughly
4. Create PR
5. Merge after approval
6. Deploy to staging

### Production Deployment

1. Ensure all tests pass
2. Update version number
3. Update CHANGELOG.md
4. Create release tag
5. Deploy to production
6. Monitor deployment

## 📚 Resources

### Documentation

- [API Documentation](http://localhost:8000/docs)
- [Database Schema](database_schema.sql)
- [Architecture Overview](docs/architecture.md)

### Tools

- [FastAPI](https://fastapi.tiangolo.com/)
- [Pytest](https://docs.pytest.org/)
- [PostgreSQL](https://www.postgresql.org/)
- [Railway](https://railway.app/)

### Communication

- **Discussions**: Use GitHub Discussions for questions
- **Issues**: Report bugs and request features
- **Email**: Contact maintainers for urgent issues

## 🎯 Contribution Areas

### High Priority

- Bug fixes
- Security improvements
- Performance optimizations
- Test coverage improvements

### Medium Priority

- New features
- Documentation improvements
- Code refactoring
- Tooling improvements

### Low Priority

- Minor UI improvements
- Code style updates
- Dependency updates

## 🏆 Recognition

Contributors will be recognized in:

- README.md contributors section
- Release notes
- Annual contributor highlights

## 📞 Getting Help

### For Contributors

- Check existing issues and discussions
- Read documentation thoroughly
- Start with small contributions
- Ask questions in discussions

### For Maintainers

- Review PRs promptly
- Provide constructive feedback
- Help new contributors get started
- Ensure code quality standards

---

Thank you for contributing to the Interview Preparation Platform! 🚀
