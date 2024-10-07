from rest_framework import serializers
from .models import Booth, BoothMenu, BoothImage
from waiting.models import Waiting

class BoothMenuSerializer(serializers.ModelSerializer):
    class Meta:
        model = BoothMenu
        fields = ['name', 'price']

class BoothListSerializer(serializers.ModelSerializer):
    thumbnail = serializers.SerializerMethodField()
    waiting_count = serializers.SerializerMethodField()
    # 사용자 대기 관련
    is_waiting = serializers.SerializerMethodField()
    waiting_status = serializers.SerializerMethodField()
    waiting_teams_ahead = serializers.SerializerMethodField()
    total_waiting_teams = serializers.SerializerMethodField()

    class Meta:
        model = Booth
        fields = ['id', 'name', 'description', 'location', 'is_operated', 'thumbnail', 'waiting_count', 'is_waiting', 'waiting_status', 'waiting_teams_ahead', 'total_waiting_teams']
    
    def get_thumbnail(self, obj):
        # 첫 번째 이미지가 썸네일 ! !
        
        # 상대 경로 반환
        # thumbnail = obj.boothimages.first()
        # if thumbnail:
        #     return thumbnail.image.url
        # return ''
        
        # 절대 경로 반환
        request = self.context.get('request')
        thumbnail = obj.boothimages.first()
        if thumbnail and request:
            return request.build_absolute_uri(thumbnail.image.url)
        return ''
    
    def get_waiting_count(self, obj):
        return obj.waitings.count()

    # 사용자 대기 관련 
    def get_is_waiting(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return Waiting.objects.filter(user=request.user, booth=obj).exists()
        return False

    def get_waiting_status(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            waiting = Waiting.objects.filter(user=request.user, booth=obj).first()
            if waiting:
                return waiting.waiting_status
        return None
    
    def get_waiting_teams_ahead(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            my_waiting = Waiting.objects.filter(user=request.user, booth=obj)
            if my_waiting:
                return Waiting.objects.filter(
                            booth=obj,
                            waiting_status__in=['waiting', 'ready_to_confirm', 'confirmed'],  
                            created_at__lt=my_waiting.created_at 
                        ).count()
        return False
        
    def get_total_waiting_teams(self, obj):
        return Waiting.objects.filter(
                booth=obj,
                waiting_status__in=['waiting', 'ready_to_confirm', 'confirmed'],  
            ).count()
    
    def to_representation(self, instance):
        # 기본 직렬화 데이터를 가져옴
        data = super().to_representation(instance)
        # 추가적인 필드 출력
        data['waiting_teams_ahead'] = self.get_waiting_teams_ahead(instance)
        data['total_waiting_teams'] = self.get_total_waiting_teams(instance)
        return data

    
class BoothImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = BoothImage
        fields = ['image']

class BoothDetailSerializer(serializers.ModelSerializer):
    menu = BoothMenuSerializer(many=True, source='menus')
    images = BoothImageSerializer(source='boothimages', many=True)
    waiting_count = serializers.SerializerMethodField()
    # 사용자 대기 관련
    is_waiting = serializers.SerializerMethodField()
    waiting_status = serializers.SerializerMethodField()
    waiting_teams_ahead = serializers.SerializerMethodField()
    total_waiting_teams = serializers.SerializerMethodField()

    class Meta:
        model = Booth
        fields = ['id', 'name', 'description', 'location', 'caution', 'is_operated', 'images', 'menu', 'open_time', 'close_time', 'waiting_count', 'is_waiting', 'waiting_status', 'waiting_teams_ahead', 'total_waiting_teams']

    def get_waiting_count(self, obj):
        return obj.waitings.count()
    
    # 사용자 대기 관련
    def get_is_waiting(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return Waiting.objects.filter(user=request.user, booth=obj).exists()
        return False

    def get_waiting_status(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            waiting = Waiting.objects.filter(user=request.user, booth=obj).first()
            if waiting:
                return waiting.waiting_status
        return None
    
    def get_waiting_teams_ahead(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            my_waiting = Waiting.objects.filter(user=request.user, booth=obj)
            if my_waiting:
                return Waiting.objects.filter(
                            booth=obj,
                            waiting_status__in=['waiting', 'ready_to_confirm', 'confirmed'],  
                            created_at__lt=my_waiting.created_at 
                        ).count()
        return False
        
    def get_total_waiting_teams(self, obj):
        return Waiting.objects.filter(
                booth=obj,
                waiting_status__in=['waiting', 'ready_to_confirm', 'confirmed'],  
            ).count()
    
    def to_representation(self, instance):
        # 기본 직렬화 데이터를 가져옴
        data = super().to_representation(instance)
        # 추가적인 필드 출력
        data['waiting_teams_ahead'] = self.get_waiting_teams_ahead(instance)
        data['total_waiting_teams'] = self.get_total_waiting_teams(instance)
        return data
