from datetime import date

from rest_framework import serializers
from MovieRestApp.models import Movie, Review, Rating, Actor
from custom.serializers import CustomSerializer


class MovieListSerializer(serializers.ModelSerializer):
    """Список Фильмов"""

    # rating_user = serializers.BooleanField()
    # middle_star = serializers.FloatField()

    class Meta:
        model = Movie
        fields = ('title', 'tagline', 'category',)


# class MovieCreateSerializer(CustomSerializer):
#     title = serializers.CharField()
#     tagline = serializers.CharField()
#     description = serializers.CharField()
#     # poster = models.ImageField(verbose_name='Постер', upload_to='movie/')
#     year = serializers.IntegerField()
#     country = serializers.CharField()
#     directors = serializers.ListSerializer(child=serializers.IntegerField())
#     actors = serializers.ListSerializer(child=serializers.IntegerField())
#     genres = serializers.ListSerializer(child=serializers.IntegerField())
#     world_premiere = serializers.DateField(default=date.today)
#     budget = serializers.IntegerField()
#     fees_in_usa = serializers.IntegerField()
#     fees_in_world = serializers.IntegerField()
#     category_id = serializers.IntegerField()
#     url = serializers.SlugField(required=True)
#     draft = serializers.BooleanField(default=False)
#
#     def validate_url(self, url):
#         url_exists = Movie.objects.filter(url=url)
#         if url_exists:
#             raise ValueError(f'{url} already exists')
#         return url_exists


class ReviewCreateSerializer(serializers.ModelSerializer):
    """Добавление отзывов"""

    class Meta:
        model = Review
        fields = '__all__'

# class ReviewCreateSerializer(serializers.Serializer):
#     email = serializers.EmailField()
#     name = serializers.CharField(max_length=100)
#     text = serializers.CharField(max_length=5000)
#     parent = serializers.IntegerField(required=False)
#     movie = serializers.IntegerField(required=True)



class FilterReviewListSerializer(serializers.ListSerializer):
    """Фильтр комментариев, только parents"""

    def to_representation(self, data):
        data = data.filter(parent=None)
        return super().to_representation(data)


class RecursiveSerializer(serializers.Serializer):
    """Вывод рекурсивно children"""

    def to_representation(self, value):
        """Серилизует children"""
        serializer = ReviewSerializer(value)
        # serializer = self.parent.parent.__class__(value)

        return serializer.data


class ReviewSerializer(serializers.ModelSerializer):
    """Вывод отзывов"""
    children = RecursiveSerializer(many=True)

    class Meta:
        list_serializer_class = FilterReviewListSerializer
        model = Review
        fields = ("name", "text", "children")


class CreateRatingSerializer(serializers.ModelSerializer):
    """Добавление рейтинга пользователем"""

    class Meta:
        model = Rating
        fields = ('star', 'movie')

    def create(self, validated_data):
        """Создание или обновление оценки фильма"""

        rating, created = Rating.objects.update_or_create(
            ip=validated_data.get('ip', None),
            movie=validated_data.get('movie', None),
            defaults={"star": validated_data.get('star')}
        )
        return rating


class ActorListSerializer(serializers.ModelSerializer):
    """Вывод списка актеров и режиссеров"""

    class Meta:
        model = Actor
        fields = 'id name image'.split()


class ActorDetailSerializer(serializers.ModelSerializer):
    """Вывод полной информации о актерах и режиссерах"""

    class Meta:
        model = Actor
        fields = '__all__'


class MovieDetailSerializer(serializers.ModelSerializer):
    """Полный фильм"""

    # """
    # SlugRelatedField - Выводит related обьекты ( по названию поля )
    # StringRelatedField - Вывод related в строку
    # PrimaryKeyRelatedField - Возвращает Primary Key
    # Для отображения деталей Foreign и ManytoMany Fields
    # """
    category = serializers.SlugRelatedField(slug_field='name', read_only=True)
    directors = ActorListSerializer(read_only=True, many=True)
    actors = ActorListSerializer(read_only=True, many=True)
    genres = serializers.SlugRelatedField(slug_field='name', many=True, read_only=True)
    #
    reviews = ReviewSerializer(many=True)

    class Meta:
        model = Movie
        exclude = ('draft',)  # Выводит все поля кроме draft


class DirectorUpdateValidate(CustomSerializer):
    name = serializers.CharField()
    age = serializers.IntegerField(min_value=0)
    description = serializers.CharField()
    image = serializers.ImageField(required=False)