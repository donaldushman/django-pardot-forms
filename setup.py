# setup.py
from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="django-pardot-forms",
    version="0.1.0",
    author="Donald Ushman",
    author_email="ushman@hotmail.com",
    description="Django app for Pardot-integrated contact and subscription forms with AJAX modal support",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/donaldushman/django-pardot-forms",
    packages=find_packages(),
    package_data={
        'pardot_forms': [
            'templates/pardot_forms/*.html',
            'templates/pardot_forms/includes/*.html',
            'static/pardot_forms/css/*.css',
            'static/pardot_forms/js/*.js',
            'migrations/*.py',
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Framework :: Django",
        "Framework :: Django :: 4.0",
        "Framework :: Django :: 4.1",
        "Framework :: Django :: 4.2",
        "Framework :: Django :: 5.0",
        "Framework :: Wagtail",
        "Framework :: Wagtail :: 5",
        "Framework :: Wagtail :: 6",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
    ],
    keywords="django pardot forms contact subscription turnstile cloudflare wagtail",
    python_requires=">=3.8",
    install_requires=[
        "Django>=4.0",
        "requests>=2.25.0",
        "django-turnstile>=0.1.0",
    ],
    extras_require={
        "wagtail": [
            "wagtail>=5.0",
        ],
    },
    zip_safe=False,
)