from django.contrib import admin
from django.utils.safestring import mark_safe
from django import forms
from MovieRestApp.models import (Category,
                          Actor,
                          Genre,
                          Movie,
                          MovieShorts,
                          Rating,
                          Review,
                          RatingStar)


# Register your models here.

from ckeditor_uploader.widgets import CKEditorUploadingWidget


class MovieAdminForm(forms.ModelForm):
    description = forms.CharField(label='Описание',widget=CKEditorUploadingWidget())
    class Meta:
        model = Movie
        fields = '__all__'

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    '''Категории'''
    list_display = ('id', 'name', 'url')
    list_display_links = ('name',)


class ReviewInline(admin.TabularInline):
    '''Создание класса для отображения всех отзывов
             к определенному фильму'''
    model = Review
    readonly_fields = ('name', 'email')
    extra = 0

class MovieShotsInline(admin.TabularInline):
    '''Создание класса для отображения всех кадров
             к определенному фильму'''
    model = MovieShorts
    extra = 0
    readonly_fields = ('get_image',)

    '''Метод для отображения изображение в панели'''
    def get_image(self, obj):
        return mark_safe(f'<img src ={obj.image.url} width="100" height="110">')

    get_image.short_description = 'Изображение'

@admin.register(Movie)
class MovieAdmin(admin.ModelAdmin):
    '''Фильмы'''
    list_display = ('title', 'category', 'url', 'draft')
    list_filter = ('category',)  # Для фильтрации
    search_fields = ('title', 'category__name')  # Поля для поиска /
    # __'название поля' чтобы передать по какому полю категории искать
    inlines = [MovieShotsInline,ReviewInline]
    save_on_top = True  # добавить кнопку SAVE на вверх панели
    save_as = True  # Сохранить данную запись как новый обьект
    list_editable = ('draft',)
    actions = ['publish','unpublish']
    # fields = ('title',) # fields - Поля для отображения в панеле редактирования
    readonly_fields = ('get_poster',)
    form = MovieAdminForm
    fieldsets = [  # При использовании ((...),) Поля отображаются в линию
        (None, {
            'fields': (('title', 'tagline'),)
        }),
        (None, {
            'fields': ('description', 'poster','get_poster')
        }),
        (None, {
            'fields': (('year', 'world_premiere', 'country'),)
        }),
        ('Actors', {  # Actors - Название группы
            'classes': ('collapse',),  # Для возможности свернуть группу
            'fields': (('actors', 'directors', 'genres', 'category'),)
        }),
        (None, {
            'fields': (('budget', 'fees_in_usa', 'fees_in_world'),)
        }),
        (None, {
            'fields': (('url', 'draft'),)
        }),
    ]
    def get_poster(self, obj):
        return mark_safe(f'<img src ={obj.poster.url} width="100" height="110">')

    get_poster.short_description = 'Изображение'

    def unpublish(self, request, queryset):
        '''Снять с публикации'''
        row_update = queryset.update(draft=0)
        if row_update == 1:
            message_bit = '1 запись была обновлена'
        else:
            message_bit = f'{row_update} записей были обновлены'
        self.message_user(request,f'{message_bit}')

    def publish(self, request, queryset):
        '''Опубликовать'''
        row_update = queryset.update(draft=1)
        if row_update == 1:
            message_bit = '1 запись была обновлена'
        else:
            message_bit = f'{row_update} записей были обновлены'
        self.message_user(request,f'{message_bit}')

    publish.short_description = 'Опубликовать'
    publish.allowed_permissions = ('change',)

    unpublish.short_description = 'Снять с публикации'
    unpublish.allowed_permissions = ('change',)

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    '''Отзывы'''
    list_display = ('name', 'email', 'parent', 'movie', 'id')
    # readonly_fields = ('name', 'email')  # Скрытие полей, предотвращение от изменений


@admin.register(Actor)
class ActorAdmin(admin.ModelAdmin):
    '''Актеры'''
    list_display = ('name', 'age', 'get_image')
    readonly_fields = ('get_image',)

    '''Метод для отображения изображение в панели'''
    def get_image(self, obj):
        return mark_safe(f'<img src ={obj.image.url} width="100" height="110">')

    get_image.short_description = 'Изображение'


@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    '''Жанры'''
    list_display = ('name', 'url')


@admin.register(Rating)
class RatingAdmin(admin.ModelAdmin):
    '''Рейтинг'''
    list_display = ('ip', 'star', 'movie')


@admin.register(MovieShorts)
class MovieShortsAdmin(admin.ModelAdmin):
    '''Отрывки из фильма'''
    list_display = ('title', 'movie','get_image')
    readonly_fields = ('get_image',)

    '''Метод для отображения изображение в панели'''
    def get_image(self, obj):
        return mark_safe(f'<img src ={obj.image.url} width="100" height="110">')

    get_image.short_description = 'Изображение'


admin.site.site_title = 'Django Movies'
admin.site.site_header = 'Django Movies'

@admin.register(RatingStar)
class RatingStarAdmin(admin.ModelAdmin):
    list_display = ('value',)