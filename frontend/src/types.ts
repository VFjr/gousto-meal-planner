export interface RecipeImage {
    width: number;
    url: string;
    id: number;
}

export interface Ingredient {
    name: string;
    id: number;
    images: RecipeImage[];
}

export interface RecipeIngredient {
    amount: string;
    ingredient: Ingredient;
}

export interface InstructionStep {
    text: string;
    order: number;
    recipe_id: number;
    id: number;
    images: RecipeImage[];
}

export interface Recipe {
    title: string;
    slug: string;
    gousto_uid: string;
    rating: number;
    prep_time: number;
    id: number;
    basic_ingredients: string[];
    instruction_steps: InstructionStep[];
    images: RecipeImage[];
    ingredients: RecipeIngredient[];
}

export type SearchType = 'url' | 'name' | 'ingredient'; 