export interface RecipeImage {
    width: number;
    url: string;
    id: number;
}

export interface Recipe {
    title: string;
    slug: string;
    gousto_uid: string;
    rating: number;
    prep_time: number;
    id: number;
    basic_ingredients: string[];
    instruction_steps: string[];
    images: RecipeImage[];
    ingredients: string[];
}

export type SearchType = 'url' | 'name' | 'ingredient'; 