import { Recipe } from '../types';
import { getProxiedImageUrl } from '../utils/image';
import { useEffect, useState, useRef } from 'react';
import { PDFDownloadLink, Document, Page } from '@react-pdf/renderer';
import RecipePDF from './RecipePDF';
import './RecipeCard.css';

interface RecipeCardProps {
    recipe: Recipe;
    isSingleRecipe?: boolean;
}

interface ImageData {
    main: string | null;
    ingredients: { [key: number]: string };
    instructions: { [key: number]: string };
}

export function RecipeCard({ recipe, isSingleRecipe = false }: RecipeCardProps) {
    const [imageUrl, setImageUrl] = useState<string>('');
    const [isExpanded, setIsExpanded] = useState(isSingleRecipe);
    const [isPdfLoading, setIsPdfLoading] = useState(false);
    const [pdfImages, setPdfImages] = useState<ImageData | null>(null);
    const [pdfDocument, setPdfDocument] = useState<React.ReactNode | null>(null);

    useEffect(() => {
        getProxiedImageUrl(recipe.images)
            .then(url => setImageUrl(url))
            .catch(() => setImageUrl(''));
    }, [recipe.images]);

    useEffect(() => {
        setIsExpanded(isSingleRecipe);
    }, [isSingleRecipe]);

    useEffect(() => {
        if (pdfImages) {
            setPdfDocument(<RecipePDF recipe={recipe} images={pdfImages} />);
        }
    }, [pdfImages, recipe]);

    const handleCookbookClick = () => {
        window.open(`https://www.gousto.co.uk/cookbook/recipes/${recipe.slug}`, '_blank');
    };

    const handleCardClick = () => {
        if (!isSingleRecipe) {
            setIsExpanded(!isExpanded);
        }
    };

    const loadPdfImages = async () => {
        if (pdfImages) {
            return;
        }

        console.log('Loading PDF images...');
        setIsPdfLoading(true);
        try {
            const blobToBase64 = (blob: Blob): Promise<string> => {
                return new Promise((resolve) => {
                    const reader = new FileReader();
                    reader.onloadend = () => resolve(reader.result as string);
                    reader.readAsDataURL(blob);
                });
            };

            // Load main recipe image
            let mainImageData: string | null = null;
            try {
                if (recipe.images?.length) {
                    const mainImageUrl = await getProxiedImageUrl(recipe.images);
                    const mainResponse = await fetch(mainImageUrl);
                    if (mainResponse.ok) {
                        const mainBlob = await mainResponse.blob();
                        mainImageData = await blobToBase64(mainBlob);
                    }
                }
            } catch (error) {
                console.error('Error loading main image:', error);
            }

            // Load ingredient images
            const ingredientImagesMap: { [key: number]: string } = {};
            if (recipe.ingredients?.length) {
                const ingredientPromises = recipe.ingredients.map(async (recipeIngredient) => {
                    try {
                        if (recipeIngredient.ingredient.images?.length) {
                            const imageUrl = await getProxiedImageUrl(recipeIngredient.ingredient.images);
                            const response = await fetch(imageUrl);
                            if (response.ok) {
                                const blob = await response.blob();
                                const base64 = await blobToBase64(blob);
                                return [recipeIngredient.ingredient.id, base64] as [number, string];
                            }
                        }
                    } catch (error) {
                        console.error(`Error loading ingredient image for ${recipeIngredient.ingredient.name}:`, error);
                    }
                    return null;
                });

                const results = await Promise.all(ingredientPromises);
                results.forEach(result => {
                    if (result) {
                        const [id, base64] = result;
                        ingredientImagesMap[id] = base64;
                    }
                });
            }

            // Load instruction step images
            const instructionImagesMap: { [key: number]: string } = {};
            if (recipe.instruction_steps?.length) {
                const instructionPromises = recipe.instruction_steps.map(async (step) => {
                    try {
                        if (step.images?.length) {
                            const imageUrl = await getProxiedImageUrl(step.images);
                            const response = await fetch(imageUrl);
                            if (response.ok) {
                                const blob = await response.blob();
                                const base64 = await blobToBase64(blob);
                                return [step.id, base64] as [number, string];
                            }
                        }
                    } catch (error) {
                        console.error(`Error loading instruction image for step ${step.order}:`, error);
                    }
                    return null;
                });

                const results = await Promise.all(instructionPromises);
                results.forEach(result => {
                    if (result) {
                        const [id, base64] = result;
                        instructionImagesMap[id] = base64;
                    }
                });
            }

            setPdfImages({
                main: mainImageData,
                ingredients: ingredientImagesMap,
                instructions: instructionImagesMap,
            });
        } catch (error) {
            console.error('Error loading PDF images:', error);
            setPdfImages(null);
            setIsPdfLoading(false);
        }
    };

    return (
        <div
            className={`recipe-card ${isExpanded ? 'expanded' : ''} ${isSingleRecipe ? 'single' : ''}`}
            onClick={handleCardClick}
        >
            <div className="recipe-image-container">
                {imageUrl && (
                    <img
                        src={imageUrl}
                        alt={recipe.title}
                        className="recipe-image"
                    />
                )}
            </div>
            <div className="recipe-content">
                <h2 className="recipe-title">{recipe.title}</h2>
                <div className="recipe-meta">
                    <span>⏱️ {recipe.prep_time} mins</span>
                    <span>⭐ {recipe.rating?.toFixed(1) ?? 'N/A'}</span>
                </div>

                {isExpanded && (
                    <div className="recipe-actions" onClick={e => e.stopPropagation()}>
                        <button
                            className="action-button cookbook-button"
                            onClick={handleCookbookClick}
                        >
                            📖 View in Cookbook
                        </button>
                        {!isPdfLoading && !pdfImages ? (
                            <button
                                className="action-button pdf-button"
                                onClick={() => {
                                    setIsPdfLoading(true);
                                    loadPdfImages();
                                }}
                            >
                                📄 Generate PDF
                            </button>
                        ) : pdfImages && pdfDocument ? (
                            <PDFDownloadLink
                                document={pdfDocument}
                                fileName={`${recipe.title}.pdf`}
                                className="action-button pdf-button"
                            >
                                {({ loading }) => (
                                    <button
                                        className="action-button pdf-button"
                                        disabled={loading}
                                    >
                                        📄 {loading ? 'Preparing PDF...' : 'Download PDF'}
                                    </button>
                                )}
                            </PDFDownloadLink>
                        ) : (
                            <button className="action-button pdf-button" disabled>
                                📄 Preparing PDF...
                            </button>
                        )}
                    </div>
                )}
            </div>
        </div>
    );
} 