import { Recipe } from '../types';
import { BACKEND_URL } from '../config';

export async function getRecipeBySlug(slug: string): Promise<Recipe> {
    const baseUrl = BACKEND_URL.replace(/\/+$/, '');

    const response = await fetch(`${baseUrl}/recipes/slug/${slug}`, {
        method: 'GET',
        headers: {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
        },
    });

    if (!response.ok) {
        if (response.status === 404) {
            throw new Error('Recipe not found');
        }
        throw new Error(`Failed to fetch recipe: ${response.statusText}`);
    }

    return response.json();
} 