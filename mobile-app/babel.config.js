module.exports = function (api) {
  api.cache(true);
  return {
    presets: ["babel-preset-expo"],
    plugins: [
      "nativewind/babel",
      "react-native-reanimated/plugin",
      "transform-inline-environment-variables",
      [
        "module-resolver",
        {
          alias: {
            "@": "./src",
            "react-native-vector-icons": "@expo/vector-icons",
          },
        },
      ],
    ],
    env: {
      production: {
        plugins: ["react-native-paper/babel"],
      },
    },
  };
};
