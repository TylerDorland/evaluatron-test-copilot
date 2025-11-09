# Contributing to Evaluatron

Thank you for your interest in contributing to Evaluatron! This document provides guidelines and instructions for contributing.

## Code of Conduct

- Be respectful and inclusive
- Provide constructive feedback
- Focus on what is best for the community
- Show empathy towards other contributors

## How to Contribute

### Reporting Bugs

1. Check if the bug has already been reported in Issues
2. If not, create a new issue with:
   - Clear, descriptive title
   - Steps to reproduce
   - Expected vs actual behavior
   - Environment details (OS, Python version, etc.)
   - Screenshots if applicable

### Suggesting Enhancements

1. Check if the enhancement has been suggested
2. Create an issue with:
   - Clear description of the enhancement
   - Use cases and benefits
   - Possible implementation approach
   - Any drawbacks or concerns

### Pull Requests

1. **Fork the repository**
   ```bash
   git clone https://github.com/yourusername/evaluatron-test-copilot.git
   cd evaluatron-test-copilot
   ```

2. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

3. **Make your changes**
   - Follow the coding standards
   - Write or update tests
   - Update documentation

4. **Run tests**
   ```bash
   cd backend
   pytest app/tests/ -v
   ```

5. **Commit your changes**
   ```bash
   git add .
   git commit -m "Add: brief description of your changes"
   ```

6. **Push to your fork**
   ```bash
   git push origin feature/your-feature-name
   ```

7. **Create a Pull Request**
   - Provide a clear description
   - Link related issues
   - Add screenshots for UI changes

## Development Setup

### Backend Development

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run development server
uvicorn app.main:app --reload

# Run tests
pytest app/tests/ -v
```

### Frontend Development

```bash
cd frontend

# Install dependencies
npm install

# Run development server
npm start

# Run tests
npm test

# Build for production
npm run build
```

## Coding Standards

### Python (Backend)

- Follow PEP 8 style guide
- Use type hints where appropriate
- Write docstrings for functions and classes
- Maximum line length: 100 characters
- Use meaningful variable names

Example:
```python
from typing import List, Optional

def get_queries(
    user_id: int,
    limit: int = 100,
    status: Optional[str] = None
) -> List[LLMQuery]:
    """
    Retrieve queries for a specific user.
    
    Args:
        user_id: The ID of the user
        limit: Maximum number of queries to return
        status: Filter by query status
        
    Returns:
        List of LLMQuery objects
    """
    # Implementation
    pass
```

### JavaScript/React (Frontend)

- Use functional components with hooks
- Follow Airbnb JavaScript Style Guide
- Use meaningful component and variable names
- Keep components small and focused
- Write PropTypes or TypeScript types

Example:
```javascript
import React, { useState, useEffect } from 'react';

function QueryList({ userId, onQuerySelect }) {
  const [queries, setQueries] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadQueries();
  }, [userId]);

  const loadQueries = async () => {
    // Implementation
  };

  return (
    // JSX
  );
}

export default QueryList;
```

## Testing Guidelines

- Write tests for new features
- Maintain existing test coverage
- Test both happy path and error cases
- Use descriptive test names
- Mock external services

Example:
```python
def test_user_can_create_query_with_valid_data(auth_token):
    """Test that authenticated user can create a query with valid data"""
    response = client.post(
        "/api/queries/",
        headers={"Authorization": f"Bearer {auth_token}"},
        json={"prompt": "Test", "llm_provider": "openai"}
    )
    assert response.status_code == 200
    assert response.json()["prompt"] == "Test"
```

## Documentation

- Update README.md for user-facing changes
- Update API_DOCUMENTATION.md for API changes
- Update DEPLOYMENT.md for infrastructure changes
- Add inline comments for complex logic
- Update TESTING.md for new test categories

## Commit Message Format

Use clear, descriptive commit messages:

```
Type: Brief description (50 chars or less)

More detailed explanation if needed. Wrap at 72 characters.
Include context about the problem being solved.

- Bullet points are okay
- Use present tense: "Add feature" not "Added feature"

Closes #123
```

Types:
- `Add`: New feature
- `Fix`: Bug fix
- `Update`: Update existing feature
- `Remove`: Remove feature or code
- `Refactor`: Code refactoring
- `Test`: Add or update tests
- `Docs`: Documentation changes
- `Style`: Code style changes (formatting, etc.)

## Review Process

1. Automated checks run (tests, linting)
2. Code review by maintainers
3. Address feedback if needed
4. Merge when approved

## Questions?

- Open an issue for questions
- Check existing documentation
- Reach out to maintainers

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

Thank you for contributing! 🎉
