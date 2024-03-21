
class Tools:

    @staticmethod
    def load_env_from_yaml():
        with open("../env.yaml", 'r+') as file:
            env = yaml.safe_load(file)
        return env