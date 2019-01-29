from rocketchat_API import rocketchat
# github 上的 rocket api 有点旧 更新些东西


class RocketChat (rocketchat.RocketChat):
    def channels_list(self, **kwargs):
        """Retrieves all of the channels from the server."""
        return self.__call_api_get('permissions.list', kwargs=kwargs)

