import { CORS_PROXY_URL } from '../config';
import { RecipeImage } from '../types';

export async function getProxiedImageUrl(images: RecipeImage[] | undefined, targetWidth: number = 700): Promise<string> {
    if (!images?.length) {
        return ''; // or return a default image URL
    }

    // Find the image closest to target width
    const bestImage = images.reduce((prev, curr) => {
        return Math.abs(curr.width - targetWidth) < Math.abs(prev.width - targetWidth) ? curr : prev;
    });

    const strippedImageUrl = bestImage.url
        .replace(/^https:\/\//, '')
        .replace(/(\.[a-z]+)(\/|$)/, '$1:443$2');

    const response = await fetch(CORS_PROXY_URL + strippedImageUrl, {
        headers: {
            'origin': window.location.origin,
            'x-requested-with': 'XMLHttpRequest'
        }
    });

    if (!response.ok) {
        return ''; // or return a default image URL
    }

    const blob = await response.blob();
    return URL.createObjectURL(blob);
} 