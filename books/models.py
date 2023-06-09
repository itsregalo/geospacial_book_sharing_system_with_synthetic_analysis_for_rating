from django.db import models
from accounts.models import User
import uuid
from django.contrib.gis.db import models as gis_models
from django.utils.text import slugify
# imagekit
from imagekit.models import ImageSpecField
from imagekit.processors import ResizeToFill
from django.urls import reverse

class BookOwner(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    location = gis_models.PointField(null=True, blank=True)
    address = models.CharField(max_length=200, null=True, blank=True)
    city = models.CharField(max_length=200, null=True, blank=True)

    class Meta:
        db_table = 'book_owner'

    def __str__(self):
        return self.user.email

    def get_absolute_url(self):
        return reverse('books:member_books', kwargs={'member_id': self.id})
    
class BookCategory(models.Model):
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True, blank=True)
    book_count = models.PositiveIntegerField(default=0)

    class Meta:
        db_table = 'book_category'
        verbose_name_plural = 'book categories'

    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        return super(BookCategory, self).save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('books:category_books', kwargs={'category_slug': self.slug})

class Book(models.Model):
    title = models.CharField(max_length=200)
    author = models.CharField(max_length=200, blank=True, null=True)
    category = models.ForeignKey(BookCategory, on_delete=models.CASCADE)
    description = models.TextField(blank=True, null=True)
    cover_image = models.ImageField(upload_to='book_covers/')
    cover_image_thumbnail = ImageSpecField(source='cover_image', processors=[ResizeToFill(293, 440)], 
                                           format='JPEG', options={'quality': 60})
    owner = models.ForeignKey(BookOwner, on_delete=models.CASCADE)
    location = gis_models.PointField(null=True, blank=True)
    slug = models.SlugField(max_length=200, unique=True, blank=True)
    uuid = models.UUIDField(unique=True, editable=False)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['title']
        db_table = 'book'

    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        if not self.uuid:
            self.uuid = uuid.uuid4()
        if not self.slug:
            self.slug = slugify(self.title) + '-' + self.owner.user.email.split('@')[0]
        if not self.location:
            try:
                self.location = self.owner.location
            except:
                pass

        return super(Book, self).save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('books:book_detail', kwargs={'book_id': self.id})
    

class Review(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.PositiveIntegerField(choices=((1, '1 star'), (2, '2 stars'), (3, '3 stars'), (4, '4 stars'), (5, '5 stars')))
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    sentiment_score = models.FloatField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']
        db_table = 'review'

    def __str__(self):
        return self.comment

class BorrowRequest(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    borrower = models.ForeignKey(User, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=(('pending', 'Pending'), ('approved', 'Approved'), ('rejected', 'Rejected')))
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'borrow_request'

    def __str__(self):
        return self.book.title
    
class LendRequest(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    lender = models.ForeignKey(User, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=(('pending', 'Pending'), ('approved', 'Approved'), ('rejected', 'Rejected')))
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'lend_request'

    def __str__(self):
        return self.book.title
    

class BookReviewSentiment(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    review = models.OneToOneField(Review, on_delete=models.CASCADE)
    text = models.TextField(blank=True, null=True)
    sentiment_score = models.FloatField(null=True, blank=True)

    class Meta:
        db_table = 'book_review_sentiment'

    def __str__(self):
        return self.text