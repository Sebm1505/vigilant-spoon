# books.py - Enhanced book data for the e-library application

all_books = [
    {
        'id': 1,
        'title': 'Accomplice to the Villain',
        'author': 'Hannah Nicole Maehrer',
        'category': 'Adult',
        'isbn': '9780593642139',
        'publication_year': 2024,
        'publisher': 'Red Tower Books',
        'pages': 482,
        'cover_image': 'https://images-na.ssl-images-amazon.com/images/S/compressed.photo.goodreads.com/books/1695659741i/123395625.jpg',
        'description': 'Once Upon a Time meets The Office in Hannah Nicole Maehrer\'s laugh-out-loud viral TikTok series turned novel, about the sunshine assistant to an Evil Villain...and their unexpected romance. A magical office comedy with grumpy bosses, snarky frogs, and definitely-not-feelings.'
    },
    {
        'id': 2,
        'title': 'Atomic Habits: An Easy & Proven Way to Build Good Habits & Break Bad Ones',
        'author': 'James Clear',
        'category': 'Adult',
        'isbn': '9780735211292',
        'publication_year': 2018,
        'publisher': 'Avery',
        'pages': 319,
        'cover_image': 'https://images-na.ssl-images-amazon.com/images/S/compressed.photo.goodreads.com/books/1655988385i/40121378.jpg',
        'description': 'No matter your goals, Atomic Habits offers a proven framework for improving—every day. James Clear, one of the world\'s leading experts on habit formation, reveals practical strategies that will teach you exactly how to form good habits, break bad ones, and master the tiny behaviors that lead to remarkable results.'
    },
    {
        'id': 3,
        'title': 'Harry Potter and the Philosopher\'s Stone',
        'author': 'J.K. Rowling',
        'category': 'Children',
        'isbn': '9780747532699',
        'publication_year': 1997,
        'publisher': 'Bloomsbury',
        'pages': 223,
        'cover_image': 'https://images-na.ssl-images-amazon.com/images/S/compressed.photo.goodreads.com/books/1598823299i/42844155.jpg',
        'description': 'Harry Potter has no idea how famous he is. That\'s because he\'s being raised by his miserable aunt and uncle who are terrified Harry will learn that he\'s a wizard, just as his parents were. But everything changes when Harry is summoned to attend an infamous school for wizards, and he begins to discover some clues about his illustrious birthright.'
    },
    {
        'id': 4,
        'title': 'The Hunger Games',
        'author': 'Suzanne Collins',
        'category': 'Teens',
        'isbn': '9780439023528',
        'publication_year': 2008,
        'publisher': 'Scholastic Press',
        'pages': 374,
        'cover_image': 'https://images-na.ssl-images-amazon.com/images/S/compressed.photo.goodreads.com/books/1586722975i/2767052.jpg',
        'description': 'In the ruins of a place once known as North America lies the nation of Panem, a shining Capitol surrounded by twelve outlying districts. When sixteen-year-old Katniss Everdeen steps forward to take her younger sister\'s place in the games, she sees it as a death sentence. But Katniss has been close to dead before and survival, for her, is second nature.'
    },
    {
        'id': 5,
        'title': 'To Kill a Mockingbird',
        'author': 'Harper Lee',
        'category': 'Adult',
        'isbn': '9780060935467',
        'publication_year': 1960,
        'publisher': 'J. B. Lippincott & Co.',
        'pages': 376,
        'cover_image': 'https://images-na.ssl-images-amazon.com/images/S/compressed.photo.goodreads.com/books/1553383690i/2657.jpg',
        'description': 'The story of young Scout Finch, who is growing up in the sleepy Alabama town of Maycomb in the 1930s. When her father Atticus, a lawyer, takes on the controversial case of a black man accused of rape, Scout and her brother Jem are forced to confront the harsh realities of prejudice and injustice.'
    },
    {
        'id': 6,
        'title': 'The Cat in the Hat',
        'author': 'Dr. Seuss',
        'category': 'Children',
        'isbn': '9780394800011',
        'publication_year': 1957,
        'publisher': 'Random House',
        'pages': 61,
        'cover_image': 'https://images-na.ssl-images-amazon.com/images/S/compressed.photo.goodreads.com/books/1327907920i/233093.jpg',
        'description': 'The Cat in the Hat is a children\'s book written and illustrated by Theodor Geisel under the pen name Dr. Seuss. The story centers on a tall anthropomorphic cat who wears a red and white-striped hat and a red bow tie. This beloved classic has been delighting children and adults alike for generations with its playful rhymes and imaginative illustrations.'
    },
    {
        'id': 7,
        'title': 'The Fault in Our Stars',
        'author': 'John Green',
        'category': 'Teens',
        'isbn': '9780525478812',
        'publication_year': 2012,
        'publisher': 'Dutton Books',
        'pages': 313,
        'cover_image': 'https://images-na.ssl-images-amazon.com/images/S/compressed.photo.goodreads.com/books/1360206420i/11870085.jpg',
        'description': 'Despite the tumor-shrinking medical miracle that has bought her a few years, Hazel has never been anything but terminal, her final chapter inscribed upon diagnosis. But when a gorgeous plot twist named Augustus Waters suddenly appears at Cancer Kid Support Group, Hazel\'s story is about to be completely rewritten.'
    },
    {
        'id': 8,
        'title': '1984',
        'author': 'George Orwell',
        'category': 'Adult',
        'isbn': '9780451524935',
        'publication_year': 1949,
        'publisher': 'Secker & Warburg',
        'pages': 328,
        'cover_image': 'https://images-na.ssl-images-amazon.com/images/S/compressed.photo.goodreads.com/books/1657781256i/61439040.jpg',
        'description': 'Winston Smith works for the Ministry of Truth in London, chief city of Airstrip One. Big Brother stares out from every poster, the Thought Police uncover every act of betrayal. This dystopian social science fiction novel presents a terrifying vision of life in the future when a totalitarian regime watches over all citizens and directs all activities.'
    },
    {
        'id': 9,
        'title': 'Percy Jackson: The Lightning Thief',
        'author': 'Rick Riordan',
        'category': 'Children',
        'isbn': '9780786838653',
        'publication_year': 2005,
        'publisher': 'Miramax Books',
        'pages': 377,
        'cover_image': 'https://images-na.ssl-images-amazon.com/images/S/compressed.photo.goodreads.com/books/1400602609i/28187.jpg',
        'description': 'Percy Jackson is a good kid, but he can\'t seem to focus on his schoolwork or control his temper. When his mother sends him to a summer camp for demigods, he learns the shocking truth: he is a son of a Greek god. Percy must master his new found skills in order to prevent a war between the gods that could devastate the entire world.'
    },
    {
        'id': 10,
        'title': 'Divergent',
        'author': 'Veronica Roth',
        'category': 'Teens',
        'isbn': '9780062024022',
        'publication_year': 2011,
        'publisher': 'Katherine Tegen Books',
        'pages': 487,
        'cover_image': 'https://images-na.ssl-images-amazon.com/images/S/compressed.photo.goodreads.com/books/1618526618i/13335037.jpg',
        'description': 'In Beatrice Prior\'s dystopian Chicago world, society is divided into five factions, each dedicated to the cultivation of a particular virtue. On an appointed day of every year, all sixteen-year-olds must select the faction to which they will devote the rest of their lives. But Tris chooses a dangerous secret that will change her life forever.'
    }
]