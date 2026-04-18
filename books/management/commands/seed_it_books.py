"""
Management command to seed 500 IT-based books.
Run: python manage.py seed_it_books
"""
from django.core.management.base import BaseCommand
from books.models import Book, Category
import random


class Command(BaseCommand):
    help = 'Seeds the database with 500 IT-based books'

    def handle(self, *args, **options):
        self.stdout.write('Seeding 500 IT books...')

        # Create IT categories
        it_categories_data = [
            ('Programming', 'Programming languages and software development'),
            ('Web Development', 'Frontend, backend, and full-stack web development'),
            ('Data Science', 'Machine learning, AI, and data analysis'),
            ('Cybersecurity', 'Network security, ethical hacking, and cryptography'),
            ('Cloud Computing', 'AWS, Azure, Google Cloud, and DevOps'),
            ('Mobile Development', 'iOS, Android, and cross-platform development'),
            ('Database', 'SQL, NoSQL, and database management'),
            ('Networking', 'Computer networks and protocols'),
            ('Operating Systems', 'Linux, Windows, Unix, and system administration'),
            ('Software Engineering', 'Design patterns, architecture, and best practices'),
        ]
        
        categories = {}
        for name, desc in it_categories_data:
            cat, created = Category.objects.get_or_create(name=name, defaults={'description': desc})
            categories[name] = cat
            if created:
                self.stdout.write(f'  ✓ Created category: {name}')

        # IT Book templates with realistic data
        book_templates = [
            # Programming
            ('Python Programming', 'Python', ['Mark Lutz', 'Eric Matthes', 'Al Sweigart', 'Luciano Ramalho']),
            ('JavaScript Essentials', 'JavaScript', ['Kyle Simpson', 'Douglas Crockford', 'Marijn Haverbeke']),
            ('Java Programming', 'Java', ['Joshua Bloch', 'Kathy Sierra', 'Herbert Schildt']),
            ('C++ Programming', 'C++', ['Bjarne Stroustrup', 'Scott Meyers', 'Stanley Lippman']),
            ('Go Programming', 'Go', ['Alan Donovan', 'William Kennedy', 'Mark Summerfield']),
            ('Rust Programming', 'Rust', ['Steve Klabnik', 'Carol Nichols', 'Jim Blandy']),
            ('Ruby Programming', 'Ruby', ['David Flanagan', 'Yukihiro Matsumoto', 'Russ Olsen']),
            ('PHP Development', 'PHP', ['Luke Welling', 'Kevin Tatroe', 'Rasmus Lerdorf']),
            ('Swift Programming', 'Swift', ['Chris Lattner', 'Matt Neuburg', 'Paris Buttfield-Addison']),
            ('Kotlin Programming', 'Kotlin', ['Dmitry Jemerov', 'Svetlana Isakova', 'Antonio Leiva']),
            
            # Web Development
            ('React Development', 'Web Development', ['Alex Banks', 'Eve Porcello', 'Robin Wieruch']),
            ('Angular Development', 'Web Development', ['Brad Green', 'Shyam Seshadri', 'Yakov Fain']),
            ('Vue.js Development', 'Web Development', ['Evan You', 'Chris Fritz', 'Sarah Drasner']),
            ('Node.js Development', 'Web Development', ['Ryan Dahl', 'David Herron', 'Samer Buna']),
            ('Django Development', 'Web Development', ['William Vincent', 'Antonio Mele', 'Nigel George']),
            ('Flask Development', 'Web Development', ['Miguel Grinberg', 'Jack Stouffer', 'Gareth Dwyer']),
            ('Express.js Development', 'Web Development', ['Evan Hahn', 'Azat Mardan', 'Hage Yaapa']),
            ('HTML5 and CSS3', 'Web Development', ['Jon Duckett', 'Ben Frain', 'Laura Lemay']),
            ('RESTful API Design', 'Web Development', ['Leonard Richardson', 'Mike Amundsen', 'Sam Ruby']),
            ('GraphQL Development', 'Web Development', ['Eve Porcello', 'Alex Banks', 'Samer Buna']),
            
            # Data Science
            ('Machine Learning', 'Data Science', ['Andrew Ng', 'Sebastian Raschka', 'Aurélien Géron']),
            ('Deep Learning', 'Data Science', ['Ian Goodfellow', 'Yoshua Bengio', 'François Chollet']),
            ('Data Analysis with Python', 'Data Science', ['Wes McKinney', 'Jake VanderPlas', 'Joel Grus']),
            ('Natural Language Processing', 'Data Science', ['Steven Bird', 'Ewan Klein', 'Edward Loper']),
            ('Computer Vision', 'Data Science', ['Richard Szeliski', 'Adrian Rosebrock', 'Satya Mallick']),
            ('TensorFlow Development', 'Data Science', ['Laurence Moroney', 'Bharath Ramsundar', 'Reza Zadeh']),
            ('PyTorch Development', 'Data Science', ['Eli Stevens', 'Luca Antiga', 'Thomas Viehmann']),
            ('Data Visualization', 'Data Science', ['Edward Tufte', 'Alberto Cairo', 'Cole Nussbaumer']),
            ('Statistical Learning', 'Data Science', ['Trevor Hastie', 'Robert Tibshirani', 'Jerome Friedman']),
            ('Big Data Analytics', 'Data Science', ['Michael Minelli', 'Michele Chambers', 'Ambiga Dhiraj']),
            
            # Cybersecurity
            ('Ethical Hacking', 'Cybersecurity', ['Kevin Mitnick', 'Georgia Weidman', 'Peter Kim']),
            ('Network Security', 'Cybersecurity', ['William Stallings', 'Charlie Kaufman', 'Radia Perlman']),
            ('Cryptography', 'Cybersecurity', ['Bruce Schneier', 'Niels Ferguson', 'Douglas Stinson']),
            ('Penetration Testing', 'Cybersecurity', ['Patrick Engebretson', 'Peter Kim', 'Georgia Weidman']),
            ('Web Application Security', 'Cybersecurity', ['Dafydd Stuttard', 'Marcus Pinto', 'Bryan Sullivan']),
            ('Malware Analysis', 'Cybersecurity', ['Michael Sikorski', 'Andrew Honig', 'Monnappa K A']),
            ('Digital Forensics', 'Cybersecurity', ['Eoghan Casey', 'Brian Carrier', 'Harlan Carvey']),
            ('Security Operations', 'Cybersecurity', ['Joseph Muniz', 'Gary McIntyre', 'Nadhem AlFardan']),
            ('Cloud Security', 'Cybersecurity', ['Chris Dotson', 'Michael Roza', 'Zeal Vora']),
            ('IoT Security', 'Cybersecurity', ['Nitesh Dhanjani', 'Billy Rios', 'Brett Walkenhorst']),
            
            # Cloud Computing
            ('AWS Solutions', 'Cloud Computing', ['John Stamper', 'Mike Pfeiffer', 'Ben Piper']),
            ('Azure Development', 'Cloud Computing', ['Michael Collier', 'Robin Shahan', 'Sjoukje Zaal']),
            ('Google Cloud Platform', 'Cloud Computing', ['Dan Sullivan', 'Geewax JJ', 'Rui Costa']),
            ('Docker Containers', 'Cloud Computing', ['Jeffrey Nickoloff', 'Stephen Kuenzli', 'Elton Stoneman']),
            ('Kubernetes', 'Cloud Computing', ['Brendan Burns', 'Joe Beda', 'Kelsey Hightower']),
            ('DevOps Practices', 'Cloud Computing', ['Gene Kim', 'Jez Humble', 'Patrick Debois']),
            ('Terraform', 'Cloud Computing', ['Yevgeniy Brikman', 'James Turnbull', 'Scott Lowe']),
            ('CI/CD Pipelines', 'Cloud Computing', ['Paul Duvall', 'Steve Matyas', 'Andrew Glover']),
            ('Serverless Architecture', 'Cloud Computing', ['Peter Sbarski', 'Sam Newman', 'Yan Cui']),
            ('Microservices', 'Cloud Computing', ['Sam Newman', 'Chris Richardson', 'Martin Fowler']),
        ]

        publishers = [
            "O'Reilly Media", "Packt Publishing", "Apress", "Manning Publications",
            "Addison-Wesley", "Pearson", "Wiley", "McGraw-Hill", "No Starch Press",
            "Pragmatic Bookshelf", "MIT Press", "Springer", "Cambridge University Press"
        ]

        shelf_locations = [
            'A1', 'A2', 'A3', 'A4', 'A5', 'B1', 'B2', 'B3', 'B4', 'B5',
            'C1', 'C2', 'C3', 'C4', 'C5', 'D1', 'D2', 'D3', 'D4', 'D5'
        ]

        books_created = 0
        books_skipped = 0

        # Generate 500 books
        for i in range(500):
            template = book_templates[i % len(book_templates)]
            title_base, category_name, authors = template
            
            # Create variations of titles
            variations = [
                f"{title_base}: A Comprehensive Guide",
                f"Mastering {title_base}",
                f"{title_base} for Beginners",
                f"Advanced {title_base}",
                f"{title_base} in Action",
                f"Learning {title_base}",
                f"Professional {title_base}",
                f"{title_base} Cookbook",
                f"{title_base} Best Practices",
                f"Practical {title_base}",
            ]
            
            title = variations[i % len(variations)]
            author = authors[i % len(authors)]
            
            # Generate unique ISBN
            isbn = f"978{random.randint(0, 9)}{random.randint(100000000, 999999999)}"
            
            # Check if ISBN already exists
            if Book.objects.filter(isbn=isbn).exists():
                books_skipped += 1
                continue
            
            category = categories.get(category_name)
            publisher = publishers[i % len(publishers)]
            year = random.randint(2015, 2024)
            quantity = random.randint(2, 10)
            shelf = shelf_locations[i % len(shelf_locations)]
            
            # Create description
            descriptions = [
                f"A comprehensive guide to {title_base.lower()} covering fundamental concepts and advanced techniques.",
                f"Learn {title_base.lower()} from scratch with practical examples and real-world projects.",
                f"Master {title_base.lower()} with this in-depth resource for developers and IT professionals.",
                f"Explore the latest features and best practices in {title_base.lower()}.",
                f"A practical approach to {title_base.lower()} with hands-on exercises and case studies.",
            ]
            description = descriptions[i % len(descriptions)]
            
            try:
                Book.objects.create(
                    title=title,
                    author=author,
                    isbn=isbn,
                    category=category,
                    publisher=publisher,
                    publication_year=year,
                    description=description,
                    total_quantity=quantity,
                    available_quantity=quantity,
                    shelf_location=shelf,
                )
                books_created += 1
                
                if books_created % 50 == 0:
                    self.stdout.write(f'  ✓ Created {books_created} books...')
                    
            except Exception as e:
                books_skipped += 1
                self.stdout.write(self.style.WARNING(f'  ⚠ Skipped book {i+1}: {str(e)}'))

        self.stdout.write(self.style.SUCCESS(f'\n✅ Successfully created {books_created} IT books!'))
        if books_skipped > 0:
            self.stdout.write(self.style.WARNING(f'⚠ Skipped {books_skipped} books (duplicates or errors)'))
        self.stdout.write(f'\nTotal books in database: {Book.objects.count()}')
