import { Recipe } from '../types';
import { getProxiedImageUrl } from '../utils/image';
import { useEffect, useState, useRef } from 'react';
import { PDFDownloadLink, Document, Page } from '@react-pdf/renderer';
import { RecipePDF, ImageData, RecipePDFProps } from './RecipePDF';
import './RecipeCard.css';

interface RecipeCardProps {
    recipe: Recipe;
    isSingleRecipe?: boolean;
}

export function RecipeCard({ recipe, isSingleRecipe = false }: RecipeCardProps) {
    const [mainImageUrl, setMainImageUrl] = useState<string>('');
    const [isExpanded, setIsExpanded] = useState(isSingleRecipe);
    const [pdfImages, setPdfImages] = useState<ImageData | null>(null);
    const [pdfRequested, setPdfRequested] = useState<boolean>(false);
    const [isPdfBlobReady, setIsPdfBlobReady] = useState(false);

    // Get Main Recipe image for recipe card
    useEffect(() => {
        getProxiedImageUrl(recipe.images)
            .then(url => setMainImageUrl(url))
            .catch(() => setMainImageUrl(''));
    }, [recipe.images]);

    useEffect(() => {
        setIsExpanded(isSingleRecipe);
    }, [isSingleRecipe]);

    useEffect(() => {
        if (pdfImages) {
            // Reset blob ready state when PDF images change
            setIsPdfBlobReady(false);
        }
    }, [pdfImages]);

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
            console.log('PDF images already loaded');
            return;
        }

        console.log('Loading PDF images...');

        setPdfRequested(true);

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
                    const mainImageUrl = await getProxiedImageUrl(recipe.images, 200);
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
                            const imageUrl = await getProxiedImageUrl(recipeIngredient.ingredient.images, 200);
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
                            const imageUrl = await getProxiedImageUrl(step.images, 200);
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
            setPdfRequested(false);
        }
    };

    const handlePdfBlobReady = () => {
        setIsPdfBlobReady(true);
    };

    return (
        <div
            className={`recipe-card ${isExpanded ? 'expanded' : ''} ${isSingleRecipe ? 'single' : ''}`}
            onClick={handleCardClick}
        >
            <div className="recipe-image-container">
                {mainImageUrl && (
                    <img
                        src={mainImageUrl}
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
                        <div className="button-wrapper">
                            <button
                                className="action-button"
                                onClick={handleCookbookClick}
                            >
                                📖 View in Cookbook
                            </button>
                        </div>

                        <div className="button-wrapper">
                            {pdfImages ? (
                                <PDFDownloadLink
                                    document={<RecipePDF recipe={recipe} images={pdfImages} onBlobReady={handlePdfBlobReady} />}
                                    fileName={`${recipe.title}.pdf`}
                                    style={{ textDecoration: 'none', width: '100%' }}
                                >
                                    {/* @ts-expect-error - PDFDownloadLink types are incomplete */}
                                    {({ loading }) => (
                                        <button className="action-button" disabled={loading || !isPdfBlobReady}>
                                            📄 {loading || !isPdfBlobReady ? "Preparing PDF" : "Download PDF"}
                                        </button>
                                    )}
                                </PDFDownloadLink>
                            ) : (
                                <button
                                    className="action-button"
                                    onClick={!pdfRequested ? loadPdfImages : undefined}
                                    disabled={pdfRequested}
                                >
                                    {/* Duplicate Preparing PDF message, as can only instantiate the download link once images are ready*/}
                                    📄 {pdfRequested ? "Preparing PDF" : "Generate PDF"}
                                </button>
                            )}
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
} 