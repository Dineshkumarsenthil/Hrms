from rest_framework import serializers
from .models import Holiday


class HolidaySerializer(serializers.ModelSerializer):
    kind_label = serializers.CharField(source="get_kind_display", read_only=True)

    class Meta:
        model = Holiday
        fields = ["id", "name", "date", "kind", "kind_label", "region", "description", "is_active"]

    def validate(self, attrs):
        kind = attrs.get("kind", getattr(self.instance, "kind", Holiday.Kind.COMPANY))
        region = attrs.get("region", getattr(self.instance, "region", ""))
        if kind == Holiday.Kind.REGIONAL and not region.strip():
            raise serializers.ValidationError({"region": "Region is required for a regional holiday."})
        if kind != Holiday.Kind.REGIONAL:
            attrs["region"] = ""  # region means nothing for the other kinds

        name = attrs.get("name", getattr(self.instance, "name", ""))
        day = attrs.get("date", getattr(self.instance, "date", None))
        clash = Holiday.objects.filter(name__iexact=name, date=day)
        if self.instance:
            clash = clash.exclude(pk=self.instance.pk)
        if clash.exists():
            raise serializers.ValidationError("This holiday is already defined for that date.")
        return attrs
