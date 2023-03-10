import random
from faker import Faker
from app import db, User, Category, Post, Comment, Vote

fake = Faker()

def populate_database(num_users=10, num_categories=5, num_posts=50, num_comments=100, num_votes=200):
    # create users
    users = []
    for i in range(num_users):
        user = User(
            username=fake.user_name(),
            email=fake.email(),
            password=fake.password(),
        )
        users.append(user)
        db.session.add(user)
    db.session.commit()

    # create categories
    categories = []
    for i in range(num_categories):
        category = Category(
            name=fake.word(),
        )
        categories.append(category)
        db.session.add(category)
    db.session.commit()

    # create posts
    posts = []
    for i in range(num_posts):
        post = Post(
            title=fake.sentence(),
            content=fake.paragraph(),
            user=random.choice(users),
            category=random.choice(categories),
        )
        posts.append(post)
        db.session.add(post)
    db.session.commit()

    # create comments
    comments = []
    for i in range(num_comments):
        comment = Comment(
            content=fake.paragraph(),
            user=random.choice(users),
            post=random.choice(posts),
        )
        comments.append(comment)
        db.session.add(comment)
    db.session.commit()

    # create votes
    votes = []
    for i in range(num_votes):
        vote = Vote(
            value=random.choice([-1, 1]),
            user=random.choice(users),
            post=random.choice(posts) if random.random() < 0.8 else None,
            comment=random.choice(comments) if random.random() < 0.8 else None,
        )
        votes.append(vote)
        db.session.add(vote)
    db.session.commit()

    print(f"Populated database with {num_users} users, {num_categories} categories, {num_posts} posts, {num_comments} comments, and {num_votes} votes.")