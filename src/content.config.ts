import { defineCollection } from "astro:content";
import { file } from "astro/loaders";

const pages = defineCollection({
    loader: file("data/articles.json")
});

export const collections = { pages }